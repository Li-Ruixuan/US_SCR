"""
Offline matching of a recording made by tools/record_train.py (layout 2) into frames.csv.

The recorder saves every stream on its own, with its header stamp and its receive time:
  rgb.csv   / rgb/*.png      colour frames            (reference stream)
  depth.csv / depth_raw/*.png raw depth (depth sensor resolution, uint16, depth units)
  us.csv    / us/*.png       ultrasound frames
  pose.csv                   raw tracker stream (60 Hz)
  imu.csv                    RealSense IMU
  camera_info.json, depth_camera_info.json, depth_to_color.json (extrinsics)

This script, for every RGB frame:
  * takes the nearest depth frame within --depth-tol and aligns it to the colour image
    (depth/<idx>.png at colour resolution, same units as the raw depth, 0 = no depth);
  * takes the nearest US frame within --us-tol, and flags it as a repeat if it is
    (nearly) identical to the previous US frame inside the US crop (the scanner makes
    ~19 new images/s, the grabber delivers 25-30/s, so many grabs are repeats), and as
    "air" if the probe is off the skin (us_air: the image below the top third is at the
    flat air level; typically the first 1-2 s, while the probe is placed). The dataloader
    skips air frames, so a sweep starts once the probe touches the skin;
  * interpolates the tracker pose at the RGB stamp (linear + slerp), blank if the two
    pose samples around it are more than --pose-max-gap apart (marker occluded).
    The tracker measures at 20 Hz but the pose node publishes at 60 Hz, repeating each
    measurement 3 times; the repeats are dropped first, so the pose is interpolated
    between real measurements (stamp = first time each one was published);
and writes frames.csv with the columns the dataloader expects (timestamp, us_timestamp,
rgb, depth, us, tx..qw, us_air) plus diagnostics (depth_dt, us_dt, us_repeat, rgb_rx).
RGB frames without a depth match are left out (counted in the report).

Pose clock offset: the lag that best lines up the tracker's angular speed with the
camera gyro (same clock as the colour frames) over the whole run. --apply-sync shifts the
pose stamps by it before matching (only if the correlation is >= 0.5).

  python tools/match_streams.py data/train/run-113                 # usually run by the recorder
  python tools/match_streams.py data/train/run-113 --apply-sync    # correct the pose clock offset
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


# ----------------------------------------------------------------------------- depth alignment

def load_extrinsics(run_dir):
    """depth_to_color.json -> (R (3x3), t (3,) in mm), depth-camera points to colour-camera points."""
    e = json.load(open(run_dir / "depth_to_color.json"))
    R = np.asarray(e["rotation"], float).reshape(3, 3, order="F")   # librealsense: column-major
    t = np.asarray(e["translation"], float) * (1000.0 if e.get("translation_units", "m") == "m" else 1.0)
    if abs(np.linalg.det(R) - 1) > 1e-3:
        raise ValueError(f"{run_dir}/depth_to_color.json: rotation is not a rotation (det {np.linalg.det(R):.4f})")
    if np.linalg.norm(t) > 100:
        print(f"WARNING {run_dir.name}: depth->colour baseline {np.linalg.norm(t):.0f} mm looks wrong (RealSense ~15-60 mm)")
    return R, t


ALIGN_VERSION = "2"          # bump when align_depth changes, so old depth/*.png are rebuilt


def align_depth(depth, K_d, K_c, R, t_mm, out_hw, scale_mm):
    """Reproject a raw depth image into the colour camera. Each depth pixel is splatted to
    an n x n block of colour pixels around its projection, n from the focal-length ratio
    (D435 848x480 -> 1280x720: ratio 2.2, n = 3), so neighbouring depth pixels leave no
    holes; where several land on one pixel the nearest wins. Returns uint16 in raw units."""
    H, W = out_hw
    ratio = max(K_c[0, 0] / K_d[0, 0], K_c[1, 1] / K_d[1, 1])
    n = max(1, int(np.ceil(1.1 * ratio)))         # 10 % margin for surfaces seen at an angle
    offs = range(-(n // 2), n - n // 2)
    v, u = np.nonzero(depth)
    z = depth[v, u].astype(np.float64) * scale_mm
    x = (u - K_d[0, 2]) / K_d[0, 0] * z
    y = (v - K_d[1, 2]) / K_d[1, 1] * z
    P = R @ np.stack([x, y, z]) + t_mm[:, None]
    ok = P[2] > 1e-3
    P, raw = P[:, ok], depth[v, u][ok]
    uc = K_c[0, 0] * P[0] / P[2] + K_c[0, 2]
    vc = K_c[1, 1] * P[1] / P[2] + K_c[1, 2]
    out = np.zeros((H, W), np.uint16)
    order = np.argsort(-P[2])                     # far first, so the nearest is written last
    for du in offs:
        for dv in offs:
            ui = np.rint(uc).astype(np.int64) + du
            vi = np.rint(vc).astype(np.int64) + dv
            keep = (ui >= 0) & (ui < W) & (vi >= 0) & (vi < H)
            o = order[keep[order]]
            cur = out[vi[o], ui[o]]
            new = raw[o]
            write = (cur == 0) | (new < cur)
            out[vi[o][write], ui[o][write]] = new[write]
    return out


# ----------------------------------------------------------------------------- pose interpolation

def slerp(q0, q1, u):
    q0, q1 = np.asarray(q0, float), np.asarray(q1, float)
    d = float(np.dot(q0, q1))
    if d < 0:
        q1, d = -q1, -d
    if d > 0.9995:
        q = q0 + u * (q1 - q0)
        return q / np.linalg.norm(q)
    th = np.arccos(np.clip(d, -1, 1))
    return (np.sin((1 - u) * th) * q0 + np.sin(u * th) * q1) / np.sin(th)


POSE_COLS = ["tx", "ty", "tz", "qx", "qy", "qz", "qw"]


def dedup_pose(pose):
    """Drop samples identical to the previous one (the node republishes each 20 Hz tracker
    measurement 3 times at 60 Hz); keeps the first stamp of each measurement."""
    if pose is None or len(pose) < 2:
        return pose
    X = pose[POSE_COLS].to_numpy(float)
    keep = np.r_[True, np.any(X[1:] != X[:-1], axis=1)]
    return pose[keep].reset_index(drop=True)


def interp_pose(pose, t, max_gap):
    """pose: DataFrame (timestamp, tx..qw) sorted, one row per measurement. Interpolates
    between the two samples around t if they are at most max_gap apart; None otherwise
    (marker lost, or t outside the stream)."""
    ts = pose["timestamp"].to_numpy()
    if len(ts) < 2 or t < ts[0] or t > ts[-1]:
        return None
    hi = int(np.clip(np.searchsorted(ts, t), 1, len(ts) - 1))
    lo = hi - 1
    if ts[hi] - ts[lo] > max_gap:
        return None
    a, b = pose.iloc[lo], pose.iloc[hi]
    u = 0.0 if ts[hi] == ts[lo] else float(np.clip((t - ts[lo]) / (ts[hi] - ts[lo]), 0, 1))
    xyz = [a[c] + u * (b[c] - a[c]) for c in ("tx", "ty", "tz")]
    q = slerp(a[["qx", "qy", "qz", "qw"]].to_numpy(float), b[["qx", "qy", "qz", "qw"]].to_numpy(float), u)
    return list(map(float, xyz)) + list(map(float, q))


def nearest(ts_ref, ts, tol):
    """For each reference stamp: index of the nearest stamp in ts within tol, else -1, and |dt|."""
    if len(ts) == 0:
        return np.full(len(ts_ref), -1), np.full(len(ts_ref), np.inf)
    j = np.clip(np.searchsorted(ts, ts_ref), 1, len(ts) - 1)
    j = np.where(np.abs(ts[j - 1] - ts_ref) <= np.abs(ts[j] - ts_ref), j - 1, j)
    dt = np.abs(ts[j] - ts_ref)
    return np.where(dt <= tol, j, -1), dt


# ----------------------------------------------------------------------------- US repeats, pose offset

def us_frame_flags(run_dir, us, roi, thr, min_contact_s=1.0):
    """Per US frame: (repeat, air).
    repeat: equal to the previous frame inside the crop (mean |diff| < thr grey levels; a new
      scanner image differs by speckle, ~1-3).
    air: probe off the skin at the START or END of the run (placing / lifting it): every
      frame before the first, and after the last, contact period of >= min_contact_s.
      Off-skin = the image below the top third (reverberation lines stay bright in air) is
      flat and dark: below air + 8 % of (contact - air), air = 2nd percentile, contact =
      median of the run. Weak contact in mid-sweep (little gel, probe tilted off) looks
      similar but is NOT flagged: the camera pose there is valid, and skipping it would
      split the sweep into segments that each restart from the true pose."""
    x0, y0, x1, y1 = roi
    rep, deep, prev = [], [], None
    for f in us["file"]:
        img = cv2.imread(str(run_dir / f), cv2.IMREAD_GRAYSCALE)[y0:y1, x0:x1].astype(np.float32)
        rep.append(prev is not None and float(np.abs(img - prev).mean()) < thr)
        deep.append(float(img[img.shape[0] // 3:].mean()))
        prev = img
    deep, t = np.array(deep), us["timestamp"].to_numpy(np.float64)
    air = np.zeros(len(deep), bool)
    air_lvl, contact = np.percentile(deep, 2), np.median(deep)
    if contact - air_lvl <= 3:                            # never clearly on the skin
        return rep, air.tolist()
    on = deep >= air_lvl + 0.08 * (contact - air_lvl)
    spells, i = [], 0                                     # contact periods (first, last frame)
    while i < len(on):
        j = i
        while j < len(on) and on[j] == on[i]:
            j += 1
        if on[i] and t[j - 1] - t[i] >= min_contact_s:
            spells.append((i, j - 1))
        i = j
    if spells:
        air[:spells[0][0]] = True
        air[spells[-1][1] + 1:] = True
    return rep, air.tolist()


def air_span(frames, where):
    """Seconds of contiguous air frames at the start or end of frames.csv rows."""
    a = (frames["us_air"] == 1).to_numpy()
    t = frames["timestamp"].astype(float).to_numpy()
    if not len(a) or not (a[0] if where == "start" else a[-1]):
        return 0.0
    if where == "start":
        k = int(np.argmax(~a)) if (~a).any() else len(a)
        return float(t[k - 1] - t[0])
    k = int(np.argmax(~a[::-1])) if (~a).any() else len(a)
    return float(t[-1] - t[len(a) - k])


def pose_gyro_offset(pose, imu, max_lag=0.3, hz=200.0, max_pose_gap=0.2):
    """Clock offset of the pose stream vs the camera/IMU clock: lag that best aligns the
    tracker's angular speed with |gyro| (both frame-independent). Positive: pose stamps late.
    Returns (offset_s, correlation) or (None, None)."""
    if pose is None or imu is None or len(pose) < 20 or len(imu) < 100:
        return None, None
    from scipy.spatial.transform import Rotation
    tp = pose["timestamp"].to_numpy()
    q = pose[["qx", "qy", "qz", "qw"]].to_numpy(float)
    dt = np.diff(tp)
    w = (Rotation.from_quat(q[1:]) * Rotation.from_quat(q[:-1]).inv()).magnitude() / np.maximum(dt, 1e-3)
    tw, ok = (tp[1:] + tp[:-1]) / 2, dt < max_pose_gap
    ti = imu["timestamp"].to_numpy()
    g = np.linalg.norm(imu[["gx", "gy", "gz"]].to_numpy(float), axis=1)
    k = max(1, int(round(0.05 * len(ti) / max(ti[-1] - ti[0], 1e-3))))   # ~50 ms box filter (pose is 20 Hz)
    g = np.convolve(g, np.ones(k) / k, "same")
    grid = np.arange(max(ti[0], tw[0]), min(ti[-1], tw[-1]), 1.0 / hz)
    if len(grid) < 4 * max_lag * hz:
        return None, None
    A = np.interp(grid, ti, g)
    B = np.interp(grid, tw[ok], w[ok])
    valid = np.interp(grid, tw, ok.astype(float)) > 0.99                # no pose gap around this time
    best = (None, -np.inf)
    L = int(max_lag * hz)
    for lag in range(-L, L + 1):                                         # pose(t + lag) vs gyro(t)
        a = A[max(0, -lag): len(A) - max(0, lag)]
        b = B[max(0, lag): len(B) - max(0, -lag)]
        m = valid[max(0, lag): len(B) - max(0, -lag)]
        if m.sum() < hz:
            continue
        a, b = a[m], b[m]
        c = float(np.mean((a - a.mean()) * (b - b.mean())) / (a.std() * b.std() + 1e-12))
        if c > best[1]:
            best = (lag / hz, c)
    return best if best[0] is not None else (None, None)


# ----------------------------------------------------------------------------- main

def match(run_dir, depth_tol=0.020, us_tol=0.035, pose_max_gap=0.080, repeat_thr=0.5,
          apply_sync=False, align=True, us_roi=(121, 80, 619, 440)):
    run_dir = Path(run_dir)
    rgb = pd.read_csv(run_dir / "rgb.csv").sort_values("timestamp").reset_index(drop=True)
    dep = pd.read_csv(run_dir / "depth.csv").sort_values("timestamp").reset_index(drop=True)
    us = (pd.read_csv(run_dir / "us.csv").sort_values("timestamp").reset_index(drop=True)
          if (run_dir / "us.csv").exists() else None)
    pose = dedup_pose(pd.read_csv(run_dir / "pose.csv").sort_values("timestamp").reset_index(drop=True)
                      if (run_dir / "pose.csv").exists() else None)
    imu = pd.read_csv(run_dir / "imu.csv") if (run_dir / "imu.csv").exists() else None

    if us is not None and not (run_dir / "us_roi.json").exists() and us_roi:
        json.dump({"version": 2, "start": us_roi[:2], "end": us_roi[2:],
                   "note": "TUS-REC crop of the 800x600 screen grab (see us_calibration.json); written by "
                           "match_streams.py -- check it if scanner depth, sector or zoom changed"},
                  open(run_dir / "us_roi.json", "w"), indent=2)
    if us is not None and (run_dir / "us_roi.json").exists():
        r = json.load(open(run_dir / "us_roi.json"))
        us_roi = (*r["start"], *r["end"])

    us_repeat, us_air = us_frame_flags(run_dir, us, us_roi, repeat_thr) if us is not None else ([], [])
    pose_off, pose_corr = pose_gyro_offset(pose, imu)
    shifted = apply_sync and pose_off is not None and pose_corr >= 0.5
    if shifted:
        pose["timestamp"] = pose["timestamp"] - pose_off
    elif apply_sync:
        print("  pose stamps NOT shifted: no clear gyro correlation (probe turned too little?)")

    info_c = json.load(open(run_dir / "camera_info.json"))
    raw_depth = (run_dir / "depth_camera_info.json").exists() and (run_dir / "depth_to_color.json").exists()
    n_wrong_size = 0
    if not raw_depth and {"width", "height"} <= set(dep.columns):       # aligned topic: drop raw-size frames
        ok = (dep["width"] == int(info_c["width"])) & (dep["height"] == int(info_c["height"]))
        n_wrong_size = int((~ok).sum())
        dep = dep[ok].reset_index(drop=True)

    t_rgb = rgb["timestamp"].to_numpy()
    jd, dtd = nearest(t_rgb, dep["timestamp"].to_numpy(), depth_tol)
    if us is not None:
        ju, dtu = nearest(t_rgb, us["timestamp"].to_numpy(), us_tol)
    else:
        ju, dtu = np.full(len(rgb), -1), np.full(len(rgb), np.inf)

    K_c = np.asarray(info_c["K"], float).reshape(3, 3)
    if raw_depth and align:
        info_d = json.load(open(run_dir / "depth_camera_info.json"))
        K_d = np.asarray(info_d["K"], float).reshape(3, 3)
        R, t_mm = load_extrinsics(run_dir)
        scale_mm = float(info_d.get("depth_scale", 0.001)) * 1000.0
        (run_dir / "depth").mkdir(exist_ok=True)
        stamp = run_dir / "depth" / ".align_version"
        realign = not stamp.exists() or stamp.read_text().strip() != ALIGN_VERSION

    rows, n_no_depth = [], 0
    for i, r in rgb.iterrows():
        if jd[i] < 0:
            n_no_depth += 1
            continue
        d = dep.iloc[jd[i]]
        if raw_depth and align:
            rel_depth = f"depth/{int(r['idx']):06d}.png"
            if realign or not (run_dir / rel_depth).exists():
                raw = cv2.imread(str(run_dir / d["file"]), cv2.IMREAD_UNCHANGED)
                al = align_depth(raw, K_d, K_c, R, t_mm, (int(info_c["height"]), int(info_c["width"])), scale_mm)
                cv2.imwrite(str(run_dir / rel_depth), al, [cv2.IMWRITE_PNG_COMPRESSION, 1])
        else:
            rel_depth = d["file"]                       # recorded already aligned (--aligned-depth)
        if ju[i] >= 0:
            u = us.iloc[ju[i]]
            us_file, us_t, rep, air = u["file"], f"{u['timestamp']:.9f}", int(us_repeat[ju[i]]), int(us_air[ju[i]])
        else:
            us_file, us_t, rep, air = "", "", "", ""
        p = interp_pose(pose, float(r["timestamp"]), pose_max_gap) if pose is not None else None
        pose_cells = ([f"{v:.6f}" for v in p[:3]] + [f"{v:.9f}" for v in p[3:]]) if p else [""] * 7
        rows.append([f"{r['timestamp']:.9f}", us_t, r["file"], rel_depth, us_file] + pose_cells
                    + [air, f"{dtd[i] * 1e3:.1f}", f"{dtu[i] * 1e3:.1f}" if ju[i] >= 0 else "", rep,
                       f"{r['rx']:.9f}"])
    cols = ["timestamp", "us_timestamp", "rgb", "depth", "us", "tx", "ty", "tz", "qx", "qy", "qz", "qw",
            "us_air", "depth_dt_ms", "us_dt_ms", "us_repeat", "rgb_rx"]
    out = pd.DataFrame(rows, columns=cols)
    out.to_csv(run_dir / "frames.csv", index=False)
    if raw_depth and align:
        stamp.write_text(ALIGN_VERSION)

    dt = np.diff(t_rgb) * 1e3
    n_pose = int((out["tx"] != "").sum())
    lost = []                                         # marker lost: [start (s into the run), length (s)]
    if pose is not None and len(pose) > 1:
        tp = pose["timestamp"].to_numpy()
        gp = np.diff(tp)
        lost = [[round(float(a - t_rgb[0]), 2), round(float(g), 2)] for a, g in zip(tp[:-1], gp) if g > pose_max_gap]
    report = {
        "rgb_frames": len(rgb), "frames_written": len(out), "rgb_without_depth": n_no_depth,
        "depth_wrong_size_dropped": n_wrong_size,
        "with_us": int((out["us"] != "").sum()) if us is not None else 0,
        "us_repeat_pct": 100.0 * float(np.mean(us_repeat)) if us_repeat else None,
        "us_air_s": {"start": air_span(out, "start"), "end": air_span(out, "end"),
                     "total_frames": int((out["us_air"] == 1).sum())} if us is not None else None,
        "pose_filled_pct": 100.0 * n_pose / max(len(out), 1),
        "pose_measurements": len(pose) if pose is not None else 0,
        "pose_lost": lost,
        "rgb_dt_ms": {"median": float(np.median(dt)), "p95": float(np.percentile(dt, 95)),
                      "max": float(dt.max()), "gaps_over_150ms": int((dt > 150).sum())} if len(dt) else None,
        "depth": "raw, aligned offline" if (raw_depth and align) else "as recorded",
        "tolerances_ms": {"depth": depth_tol * 1e3, "us": us_tol * 1e3, "pose": pose_max_gap * 1e3},
        "pose_offset_ms": pose_off * 1e3 if pose_off is not None else None,
        "pose_gyro_corr": pose_corr, "pose_offset_applied": shifted,
    }
    json.dump(report, open(run_dir / "match_report.json", "w"), indent=2)
    print(f"{run_dir.name}: {len(out)}/{len(rgb)} RGB frames written ({n_no_depth} without depth), "
          f"US repeats {report['us_repeat_pct'] or 0:.0f} %, "
          + (f"probe in air {report['us_air_s']['start']:.1f} s at start / {report['us_air_s']['end']:.1f} s at end, "
             if report["us_air_s"] else "") + f"pose filled {report['pose_filled_pct']:.1f} %, "
          f"RGB gaps > 150 ms: {report['rgb_dt_ms']['gaps_over_150ms'] if report['rgb_dt_ms'] else 'n/a'}")
    if lost:
        print("  marker lost: " + ", ".join(f"{a:.1f} s for {g:.2f} s" for a, g in lost[:8]))
    if pose_off is not None:
        print(f"  pose clock offset {pose_off * 1e3:+.0f} ms (gyro correlation {pose_corr:.2f})"
              + (", applied" if shifted else ""))
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", nargs="+", help="recording folders (layout 2)")
    ap.add_argument("--depth-tol", type=float, default=0.020, help="s")
    ap.add_argument("--us-tol", type=float, default=0.035,
                    help="s; > half the 67 ms gaps a 25 Hz grabber leaves, so every RGB frame keeps a US frame")
    ap.add_argument("--pose-max-gap", type=float, default=0.080,
                    help="s; max time between the two tracker measurements a frame is interpolated from "
                         "(tracker 20 Hz = 50 ms)")
    ap.add_argument("--repeat-thr", type=float, default=0.5,
                    help="mean abs grey-level difference (full resolution, US crop) below which a US frame "
                         "counts as a repeat")
    ap.add_argument("--apply-sync", action="store_true",
                    help="shift the pose stamps by the gyro-correlation offset")
    ap.add_argument("--no-align", action="store_true", help="do not align raw depth (debug)")
    ap.add_argument("--us-roi", type=int, nargs=4, default=[121, 80, 619, 440], metavar=("X0", "Y0", "X1", "Y1"),
                    help="us_roi.json written for sweeps that have none (the TUS-REC crop)")
    args = ap.parse_args()
    for r in args.runs:
        match(r, args.depth_tol, args.us_tol, args.pose_max_gap, args.repeat_thr,
              args.apply_sync, not args.no_align, tuple(args.us_roi))


if __name__ == "__main__":
    main()
