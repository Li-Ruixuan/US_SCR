"""
RGB-D SLAM baseline (e.g. ORB-SLAM3 RGB-D), scored exactly like the system without a tracker.

Two commands around the SLAM run:

  export    one session as ONE RGB-D sequence in the TUM format: the room scans first, then the sweeps
            (every frame of every run, in recording order, runs joined with a 1 s gap in time), as
            symlinks to the PNGs; associations.txt, camera.yaml (ORB-SLAM3 settings from camera_info.json)
            and index.csv (sequence time -> run, row). The SLAM system maps the room scans and must
            keep tracking or relocalise through the sweeps; nothing from Polaris goes in.
  evaluate  reads the SLAM trajectory (TUM format: t tx ty tz qx qy qz qw, metres, camera -> world) and
            scores it with the protocol of scr_map.py / scr_anchor.py track: ONE rigid alignment of the
            session plus the probe's camera calibration, both fitted on the room-scan frames against
            Polaris (or the calibration of another map fixed with --cam-calib-from, as for 4XX); the
            sweeps are never used for the fit. Writes slam_eval.md / .json (map error on the room scan,
            US-image error and frames with a pose per sweep) and poses/fold0_<sweep>_<source>.json
            (tools/us_analysis.py shape, tools/volume_figure.py).

  export DATA=/data2/u0137815/rgbd-us/data
  python tools/slam_baseline.py export --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/slam-3XX/seq
  ./Examples/RGB-D/rgbd_tum Vocabulary/ORBvoc.txt runs/slam-3XX/seq/camera.yaml runs/slam-3XX/seq runs/slam-3XX/seq/associations.txt
  python tools/slam_baseline.py evaluate --root $DATA/train_3XX --scan-runs room-301 room-302 \\
      --seq runs/slam-3XX/seq --traj CameraTrajectory.txt --out runs/slam-3XX

Frames the SLAM system did not track (lost, or in a map that was never merged) have no pose: they count in
"frames with a pose" and are left out of the errors. A sweep tracked in an unmerged map keeps its shape
(shape needs no alignment) but gets a large absolute error: that is the honest result of the protocol.
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy.spatial.transform import Rotation

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

GAP_S = 1.0          # time gap between runs in the joined sequence


def load_runs(root, scan_runs, sweeps, hand_eye):
    from dataloader import RPRConfig, RPRDataset, load_hand_eye, test_sweeps
    import scr_anchor as sa
    sweeps = sweeps or test_sweeps(root)
    T_mc = load_hand_eye(sa.resolve_hand_eye(hand_eye), "mm")
    ds = RPRDataset(root, list(scan_runs) + list(sweeps), scan_runs, RPRConfig(T_marker_cam=T_mc))
    return ds, list(sweeps), T_mc


def export(args):
    from dataloader import discover_runs
    sweeps = args.runs or [r for r in discover_runs(args.root) if not r.startswith("room-")]
    out = Path(args.out)
    for sub in ("rgb", "depth"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    from PIL import Image
    root = Path(args.root).resolve()
    assoc, index, t0 = [], [], 1.0
    for name in list(args.scan_runs) + sweeps:
        rows = list(csv.DictReader(open(root / name / "frames.csv")))
        stamps = np.array([float(r["timestamp"]) for r in rows])
        info = json.load(open(root / name / "camera_info.json"))
        wh, skipped = (int(info["width"]), int(info["height"])), 0
        for row in range(0, len(rows), args.every):
            paths = [root / name / rows[row][c] for c in ("rgb", "depth")]
            ok = all(rows[row][c] for c in ("rgb", "depth")) and all(p.is_file() for p in paths)
            if ok:
                with Image.open(paths[1]) as im:                 # depth not aligned to colour: SLAM would misread it
                    ok = im.size == wh
            if not ok:
                skipped += 1
                continue
            t = t0 + stamps[row] - stamps[0]
            k = len(index)
            for sub in ("rgb", "depth"):
                link = out / sub / f"{k:06d}.png"
                if link.is_symlink() or link.exists():
                    link.unlink()
                os.symlink(paths[0 if sub == "rgb" else 1], link)
            assoc.append(f"{t:.6f} rgb/{k:06d}.png {t:.6f} depth/{k:06d}.png")
            index.append((f"{t:.6f}", name, row))
        t0 += stamps[-1] - stamps[0] + GAP_S
        print(f"  {name}: {len(rows)} rows, every {args.every}{f', {skipped} skipped (missing or wrong-size image)' if skipped else ''}",
              flush=True)
    (out / "associations.txt").write_text("\n".join(assoc) + "\n")
    with open(out / "index.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["t", "run", "row"])
        w.writerows(index)
    info = json.load(open(root / args.scan_runs[0] / "camera_info.json"))
    K = np.asarray(info["K"], float).reshape(3, 3)
    depth_scale = float(info.get("depth_scale", 0.001))          # metres per depth unit (mm -> 0.001)
    yaml = f"""%YAML:1.0
# ORB-SLAM3 RGB-D settings written by tools/slam_baseline.py export ({args.scan_runs[0]}/camera_info.json)
File.version: "1.0"
Camera.type: "PinHole"
Camera1.fx: {K[0, 0]:.4f}
Camera1.fy: {K[1, 1]:.4f}
Camera1.cx: {K[0, 2]:.4f}
Camera1.cy: {K[1, 2]:.4f}
Camera1.k1: 0.0
Camera1.k2: 0.0
Camera1.p1: 0.0
Camera1.p2: 0.0
Camera.width: {int(info["width"])}
Camera.height: {int(info["height"])}
Camera.fps: {max(1, round(30 / args.every))}
Camera.RGB: 1
Stereo.ThDepth: 40.0
Stereo.b: 0.05
RGBD.DepthMapFactor: {1 / depth_scale:.1f}
ORBextractor.nFeatures: {args.features}
ORBextractor.scaleFactor: 1.2
ORBextractor.nLevels: 8
ORBextractor.iniThFAST: 20
ORBextractor.minThFAST: 7
Viewer.KeyFrameSize: 0.05
Viewer.KeyFrameLineWidth: 1.0
Viewer.GraphLineWidth: 0.9
Viewer.PointSize: 2.0
Viewer.CameraSize: 0.08
Viewer.CameraLineWidth: 3.0
Viewer.ViewpointX: 0.0
Viewer.ViewpointY: -0.7
Viewer.ViewpointZ: -1.8
Viewer.ViewpointF: 500.0
"""
    (out / "camera.yaml").write_text(yaml)
    print(f"{len(index)} frames ({' + '.join(args.scan_runs)} then {len(sweeps)} sweeps) -> {out}/associations.txt, "
          f"camera.yaml, index.csv")


def read_tum(path):
    """{time string (6 decimals): camera -> world, mm}."""
    poses = {}
    for line in open(path):
        v = line.split()
        if len(v) != 8 or line.startswith("#"):
            continue
        t, x = float(v[0]), np.array(v[1:], float)
        T = np.eye(4)
        T[:3, :3] = Rotation.from_quat(x[3:]).as_matrix()
        T[:3, 3] = x[:3] * 1000.0
        poses[f"{t:.6f}"] = T
    return poses


def evaluate(args):
    import scr_anchor as sa
    import scr_map as sm
    ds, sweeps, T_mc = load_runs(args.root, args.scan_runs, args.runs, args.hand_eye)
    traj = read_tum(args.traj)
    est = {n: np.full_like(ds.runs[n]["T_world_cam"], np.nan) for n in ds.runs}
    found = 0
    for t, name, row in csv.reader(list(open(Path(args.seq) / "index.csv"))[1:]):
        if name in est and t in traj:
            est[name][int(row)] = traj[t]
            found += 1
    print(f"{len(traj)} poses in {args.traj}, {found} matched to the sequence's frames")
    if not found:
        raise SystemExit("no pose matched: is --traj the trajectory of --seq (same timestamps)?")

    # 1. alignment + camera calibration on the room scan only (as scr_map.py)
    items = [(n, int(r)) for n in args.scan_runs for r in np.concatenate(ds.runs[n]["segments"])]
    gt = {n: ds.runs[n]["T_world_cam"] for n in ds.runs}
    calib = np.asarray(json.load(open(args.cam_calib_from))["cam_calib"], float) if args.cam_calib_from else not args.no_cam_calib
    A, merr, X = sm.map_errors(est, gt, items, calib=calib)
    if A is None:
        raise SystemExit("fewer than 3 room-scan frames with a SLAM pose: nothing to align")

    # 2. sweeps: A T X, optionally smoothed like the system, US-image error
    scaling, rigid = sa.read_us_calib(args.calib)
    T_cam_us = np.linalg.inv(T_mc) @ rigid
    P = T_cam_us @ scaling @ np.stack([sa.US_PX[:, 0], sa.US_PX[:, 1], np.zeros(5), np.ones(5)])
    out = Path(args.out)
    (out / "poses").mkdir(parents=True, exist_ok=True)
    res = {}
    for sw in sweeps:
        r = ds.runs[sw]
        frames, errs, segs = [], [], []
        for sid, seg in enumerate(r["segments"]):
            T = A @ est[sw][seg] @ X
            if args.smooth > 0:
                T = sa.smooth_poses(r["stamps"][seg], T, np.ones(len(seg)), args.smooth)
            segs.append(np.arange(len(errs), len(errs) + len(seg)))
            errs.extend(T)
            for x, Tn in zip(seg, T):
                us, Tg = r["df"]["us"].iloc[x], r["T_world_cam"][x]
                frames.append({"row": int(x), "segment": sid, "t": float(r["stamps"][x]), "keyframe": bool(np.isfinite(Tn).all()),
                               "rgb": r["df"]["rgb"].iloc[x], "depth": r["df"]["depth"].iloc[x], "us": us if isinstance(us, str) else None,
                               "T_world_cam_pred": Tn.tolist(), "T_world_cam_gt": Tg.tolist(),
                               "T_world_us_pred": (Tn @ T_cam_us).tolist(), "T_world_us_gt": (Tg @ T_cam_us).tolist()})
        rows = np.concatenate(r["segments"])
        err, st = sa.us_errors(np.array(errs), r["T_world_cam"][rows], P, segs, steps=(1, 8))
        res[sw] = {"us_median": float(np.nanmedian(err)) if np.isfinite(err).any() else float("nan"),
                   "us_p90": float(np.nanpercentile(err, 90)) if np.isfinite(err).any() else float("nan"),
                   "coverage_pct": float(100 * np.isfinite(err).mean()), "step_8rows": st[8]}
        doc = {"root": str(args.root), "fold": 0, "run": sw, "source": args.source, "units": "mm", "world": "Polaris",
               "chaining": f"RGB-D SLAM ({args.traj}), one alignment + camera calibration on the room scan"
                           + (f", smoothed {args.smooth:g} s" if args.smooth > 0 else ""),
               "cam_calib": X.tolist(), "T_marker_cam": T_mc.tolist(), "T_cam_us": T_cam_us.tolist(),
               "S_us_px_to_mm": scaling.tolist(), "us_roi": list(sa.load_us_roi(Path(args.root) / sw)),
               "us_pixels": "1-based on the US ROI resized to 640x480", "frames": frames}
        json.dump(doc, open(out / "poses" / f"fold0_{sw}_{args.source}.json", "w"))
        print(f"  {sw}: US median {res[sw]['us_median']:.2f} mm, {res[sw]['coverage_pct']:.0f} % of frames with a pose", flush=True)

    mean = lambda k: float(np.nanmean([v[k] for v in res.values()]))
    cal = (f"fixed from `{args.cam_calib_from}`" if args.cam_calib_from else "none" if args.no_cam_calib
           else f"fitted on the room scan: {merr.get('calib_mm', 0):.1f} mm, {merr.get('calib_deg', 0):.2f} deg")
    md = [f"# RGB-D SLAM baseline: {Path(args.root).name} (`{args.traj}`)", "",
          f"One alignment of the session and the camera calibration ({cal}) from the room-scan frames "
          f"({', '.join(args.scan_runs)}) against Polaris; the sweeps are not used for the fit. Smoothing: "
          f"{f'{args.smooth:g} s' if args.smooth > 0 else 'none (raw SLAM poses)'}.", "",
          "| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |",
          "|---|---|---|---|---|",
          f"| {merr['mapped_pct']:.0f} % | {merr['view_mm_median']:.1f} / {merr['view_mm_p90']:.1f} | {merr['pos_mm_median']:.1f} | "
          f"{merr['rot_deg_median']:.2f} | {merr['rel1s_mm_median'] or float('nan'):.1f} / {merr['rel1s_mm_p90'] or float('nan'):.1f} |", "",
          "| sweep | US image median | p90 | frames with a pose | step, 8 rows |", "|---|---|---|---|---|"]
    md += [f"| {sw} | {v['us_median']:.2f} | {v['us_p90']:.2f} | {v['coverage_pct']:.0f} % | {v['step_8rows']:.2f} |" for sw, v in res.items()]
    md += [f"| **mean** | **{mean('us_median'):.2f}** | {mean('us_p90'):.2f} | {mean('coverage_pct'):.0f} % | {mean('step_8rows'):.2f} |", "",
           f"Shape: `python tools/us_analysis.py shape --json {out}/poses/*.json --out {out}/shape.md`"]
    (out / "slam_eval.md").write_text("\n".join(md) + "\n")
    json.dump({"args": vars(args), "map": merr, "cam_calib": X.tolist(), "map_to_polaris": A.tolist(), "sweeps": res},
              open(out / "slam_eval.json", "w"), indent=1)
    print("\n".join(md) + f"\n-> {out}/slam_eval.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export", help="one session as a TUM-format RGB-D sequence (room scans, then sweeps)")
    e.add_argument("--root", required=True)
    e.add_argument("--scan-runs", nargs="+", required=True)
    e.add_argument("--runs", nargs="+", default=None, help="sweeps (default: every run-* under --root)")
    e.add_argument("--every", type=int, default=1, help="every n-th frame")
    e.add_argument("--features", type=int, default=1250, help="ORB features per frame")
    e.add_argument("--out", required=True)
    v = sub.add_parser("evaluate", help="score a SLAM trajectory of an exported sequence")
    v.add_argument("--root", required=True)
    v.add_argument("--scan-runs", nargs="+", required=True)
    v.add_argument("--runs", nargs="+", default=None, help="sweeps (default: every run-* under --root)")
    v.add_argument("--seq", required=True, help="the export folder (index.csv)")
    v.add_argument("--traj", required=True, help="SLAM trajectory, TUM format (ORB-SLAM3: CameraTrajectory.txt)")
    v.add_argument("--cam-calib-from", default=None, help="map.json whose camera calibration is used (fixed), e.g. 3XX's for 4XX")
    v.add_argument("--no-cam-calib", action="store_true", help="alignment only, no camera calibration")
    v.add_argument("--smooth", type=float, default=0.0, help="smooth the SLAM poses over this window (s), as the system (2)")
    v.add_argument("--source", default="orbslam3", help="name in the poses exports")
    v.add_argument("--calib", default=str(REPO / "calib_matrix.csv"))
    v.add_argument("--hand-eye", default=str(REPO / "T_marker_cam.npy"))
    v.add_argument("--out", required=True)
    args = ap.parse_args()
    export(args) if args.cmd == "export" else evaluate(args)


if __name__ == "__main__":
    main()
