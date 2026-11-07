"""
How good is the Polaris ground truth? Where the marker was in the tracker's measurement volume, how noisy the
tracker's own poses are at the US image, and whether our tracking error grows where Polaris is out of its volume.

The Polaris Vega measures in a pyramid in front of it, about 0.95-2.4 m along its axis (-z in its frame; 3.0 m for
the extended pyramid); its accuracy is specified only inside. Nearer than --near or farther than --far, the poses
can still be reported but may be noisy or biased. A bias there also shifts the one rigid alignment per session
that the absolute error depends on.

1. Raw stream, per recording (pose.csv, without its 60 Hz repeats; frames.csv if there is no pose.csv):
     measurements per s; distance along the Polaris axis (p5 / median / p95, mm) and off-axis angle; % of samples
     nearer than --near / farther than --far; tracker noise = residual of a 7-sample quadratic fit (Savitzky-Golay,
     350 ms at 20 Hz), corrected for the fit, at the marker origin and at the 5 US-image points (mm). It is an
     upper bound: fast hand motion adds to it. Spikes = samples whose US-image residual exceeds --spike mm.

     python tools/check_polaris.py --roots $DATA/train_3XX $DATA/train_4XX $DATA/train_5XX --out runs/polaris-check.md

2. Tracking error against the Polaris distance (with --track; needs the frames.csv and the tracking output):
     the error at the US image (smoothed --window s, as scr_anchor.py track), split by distance band and by local
     tracker noise, and the mean over sweeps of the median error on the frames inside --near..--far only.
     If the error grows near the limit while the coverage stays the same, part of it is the ground truth.

     python tools/check_polaris.py --track runs/track-v2map-5XXA-exam runs/track-v2map-3XX --out runs/polaris-track.md
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from scipy.spatial.transform import Rotation

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

US_PX = np.array([[320, 240], [160, 120], [480, 120], [160, 400], [480, 400]], float)   # scr_anchor.py US_PX
COLS = ["tx", "ty", "tz", "qx", "qy", "qz", "qw"]
SG_WIN, SG_ORDER = 7, 2
SG_C0 = savgol_filter(np.eye(SG_WIN)[SG_WIN // 2], SG_WIN, SG_ORDER, mode="interp")[SG_WIN // 2]   # centre weight


def read_us_calib(path):
    """calib_matrix.csv (TUS-REC format) -> (scaling, rigid): pixels -> US mm -> marker mm (as scr_anchor.py)."""
    rows = [l.strip().split(",") for l in open(path)]
    return np.array(rows[1:5], float), np.array(rows[6:10], float)


def us_points_marker(calib):
    """The 5 US-image points in the marker frame (4, 5), mm."""
    scaling, rigid = read_us_calib(calib)
    return rigid @ scaling @ np.stack([US_PX[:, 0], US_PX[:, 1], np.zeros(5), np.ones(5)])


def read_stream(run):
    """Tracker measurements of one recording: (t, T_polaris_marker (n, 4, 4) mm, source). Repeats and lost
    samples dropped."""
    src = run / "pose.csv" if (run / "pose.csv").exists() else run / "frames.csv"
    d = pd.read_csv(src).sort_values("timestamp").reset_index(drop=True)
    X = d[COLS].to_numpy(float)
    keep = np.r_[True, np.any(X[1:] != X[:-1], axis=1)] & np.isfinite(X).all(1)   # match_streams.py dedup_pose
    X, t = X[keep], d["timestamp"].to_numpy(float)[keep]
    if len(X) and np.nanmedian(np.abs(X[:, :3])) < 10:                            # metres -> mm
        X[:, :3] *= 1000.0
    T = np.tile(np.eye(4), (len(X), 1, 1))
    if len(X):
        T[:, :3, :3] = Rotation.from_quat(X[:, 3:]).as_matrix()
        T[:, :3, 3] = X[:, :3]
    return t, T, src.name


def segments(t, max_gap):
    """Index arrays of runs of samples without a gap longer than max_gap s."""
    cut = np.flatnonzero(np.diff(t) > max_gap) + 1
    return [s for s in np.split(np.arange(len(t)), cut) if len(s) >= SG_WIN]


def residuals(t, T, P, max_gap):
    """Per sample: residual (mm) of the marker origin and mean over the US points after the quadratic fit;
    NaN where a segment is too short."""
    pts = np.einsum("nij,jk->nik", T, P)[:, :3]                   # (n, 3, 5)
    r_m, r_us = np.full(len(t), np.nan), np.full(len(t), np.nan)
    for s in segments(t, max_gap):
        o = T[s, :3, 3]
        r_m[s] = np.linalg.norm(o - savgol_filter(o, SG_WIN, SG_ORDER, axis=0), axis=1)
        q = pts[s].reshape(len(s), -1)
        dq = (q - savgol_filter(q, SG_WIN, SG_ORDER, axis=0)).reshape(len(s), 3, -1)
        r_us[s] = np.linalg.norm(dq, axis=1).mean(1)
    return r_m, r_us


def noise(r):
    """RMS residual corrected for the fit (white noise: residual variance = sigma^2 (1 - c0))."""
    r = r[np.isfinite(r)]
    return float(np.sqrt(np.mean(r ** 2) / (1 - SG_C0))) if len(r) else float("nan")


def geometry(T):
    """Distance along the Polaris axis (mm, positive in front) and off-axis angle (deg) of the marker origin."""
    p = T[:, :3, 3]
    z = -p[:, 2]
    return z, np.degrees(np.arctan2(np.linalg.norm(p[:, :2], axis=1), z))


def raw_check(args, P):
    head = ("| recording | source | meas./s | distance mm p5 / median / p95 | off-axis deg median / p95 | "
            f"< {args.near:g} mm % | > {args.far:g} mm % | noise marker mm | **noise US image mm** | "
            f"spikes > {args.spike:g} mm /min |")
    lines, warn, sess = [], [], []
    for root in map(Path, args.roots):
        runs = sorted(p for p in root.iterdir() if p.is_dir() and p.name.split("-")[0] in ("room", "run")
                      and ((p / "pose.csv").exists() or (p / "frames.csv").exists()))
        lines += ["", f"### {root.name}", "", head, "|" + "---|" * (head.count("|") - 1)]
        per = []
        for run in runs:
            t, T, src = read_stream(run)
            if len(t) < SG_WIN:
                lines.append(f"| {run.name} | {src} | no poses | | | | | | | |")
                continue
            z, ang = geometry(T)
            r_m, r_us = residuals(t, T, P, args.max_gap)
            dur = max(t[-1] - t[0], 1e-9)
            near, far = 100 * float((z < args.near).mean()), 100 * float((z > args.far).mean())
            nm, nu = noise(r_m), noise(r_us)
            spk = float((r_us > args.spike).sum()) / (dur / 60)
            per.append(dict(name=run.name, z=float(np.median(z)), near=near, far=far, nm=nm, nu=nu, spk=spk,
                            ang=float(np.median(ang))))
            lines.append(f"| {run.name} | {src} | {len(t) / dur:.0f} | {np.percentile(z, 5):.0f} / {np.median(z):.0f} / "
                         f"{np.percentile(z, 95):.0f} | {np.median(ang):.0f} / {np.percentile(ang, 95):.0f} | {near:.0f} | "
                         f"{far:.0f} | {nm:.3f} | **{nu:.3f}** | {spk:.1f} |")
            if near > 10 or far > 10:
                warn.append(f"{root.name}/{run.name}: {near:.0f} % of the samples nearer than {args.near:g} mm, "
                            f"{far:.0f} % farther than {args.far:g} mm (outside the Polaris volume)")
            if src == "frames.csv":
                warn.append(f"{root.name}/{run.name}: no pose.csv, noise from the poses interpolated to the RGB frames "
                            "(lower than the raw tracker noise)")
        if per:
            sess.append((root.name, per))
    summ = ["| session | recordings | distance mm (median of medians) | off-axis deg | "
            f"< {args.near:g} mm % | noise marker mm | **noise US image mm** | spikes /min |", "|---|---|---|---|---|---|---|---|"]
    for name, per in sess:
        m = lambda k: float(np.median([p[k] for p in per]))
        summ.append(f"| {name} | {len(per)} | {m('z'):.0f} | {m('ang'):.0f} | {np.mean([p['near'] for p in per]):.0f} | "
                    f"{m('nm'):.3f} | **{m('nu'):.3f}** | {m('spk'):.1f} |")
    return summ + lines, warn


def track_check(args, P):
    from dataloader import RPRConfig, RPRDataset, load_hand_eye, test_sweeps
    from scr_anchor import smooth_poses, us_errors

    T_mc = load_hand_eye(REPO / "T_marker_cam.npy", "mm")
    Pc = np.linalg.inv(T_mc) @ P                                  # US points in the camera frame
    edges = [float(e) for e in args.bands]
    names = [f"< {edges[0]:g}"] + [f"{a:g}-{b:g}" for a, b in zip(edges[:-1], edges[1:])] + [f"> {edges[-1]:g}"]
    out = []
    for d in map(Path, args.track):
        a = json.load(open(d / "scr_track.json"))["args"]
        meta = json.load(open(d / "poses.json"))
        X = np.asarray(meta["cam_calib"], float) if meta.get("cam_calib") is not None else np.eye(4)
        root = Path(a["test_root"])
        ds = RPRDataset(root, test_sweeps(root, a.get("test_runs")), [], RPRConfig(T_marker_cam=T_mc, image_size=(360, 640)))
        z_npz = np.load(d / "poses.npz")
        E, Z, N, per_all, per_in = [], [], [], [], []
        for sw in ds.runs:
            r = ds.runs[sw]
            rows, T, inl = z_npz[f"{sw}_rows"], z_npz[f"{sw}_T"] @ X, z_npz[f"{sw}_inl"]
            seg_of = {int(x): k for k, s in enumerate(r["segments"]) for x in s}
            sid = np.array([seg_of[int(x)] for x in rows])
            segs = [s for s in (np.flatnonzero(sid == k) for k in range(len(r["segments"]))) if len(s) > 1]
            t = r["stamps"][rows]
            Ts = np.full_like(T, np.nan)
            for s in segs:
                Ts[s] = smooth_poses(t[s], T[s], inl[s], args.window)
            T_gt = r["T_world_cam"][rows]
            err, _ = us_errors(Ts, T_gt, Pc, segs, steps=(1,))
            z, _ = geometry(T_gt @ np.linalg.inv(T_mc))           # marker in the Polaris frame
            ts, Tr, _ = read_stream(root / sw)                     # local tracker noise around each frame
            _, r_us = residuals(ts, Tr, P, args.max_gap)
            ok = np.isfinite(r_us)
            loc = pd.Series(r_us[ok] ** 2, index=pd.to_datetime(ts[ok], unit="s")).rolling("1s", center=True).mean()
            n_loc = np.sqrt(np.interp(t, ts[ok], loc.to_numpy()) / (1 - SG_C0)) if ok.sum() > 1 else np.full(len(t), np.nan)
            f = np.isfinite(err)
            E.append(err[f]), Z.append(z[f]), N.append(n_loc[f])
            per_all.append(np.nanmedian(err))
            inside = f & (z >= args.near) & (z <= args.far)
            per_in.append(np.median(err[inside]) if inside.sum() >= args.min_frames else np.nan)
        E, Z, N = map(np.concatenate, (E, Z, N))
        band = np.digitize(Z, edges)
        out += ["", f"### {d.name} ({root.name}, smoothed {args.window:g} s)", "",
                f"All frames: **{np.nanmean(per_all):.2f}** mm (mean over sweeps of the median; scr_track.md shows the same). "
                f"Frames inside {args.near:g}-{args.far:g} mm only: **{np.nanmean(per_in):.2f}** mm "
                f"({int(np.isfinite(per_in).sum())}/{len(per_in)} sweeps with >= {args.min_frames} such frames).", "",
                "| distance band mm | frames | % | error median mm | p90 |", "|---|---|---|---|---|"]
        for k, nm in enumerate(names):
            e = E[band == k]
            if len(e):
                out.append(f"| {nm} | {len(e)} | {100 * len(e) / len(E):.0f} | {np.median(e):.2f} | {np.percentile(e, 90):.2f} |")
        q = np.nanpercentile(N, [33.3, 66.7]) if np.isfinite(N).any() else [np.nan, np.nan]
        out += ["", "| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |", "|---|---|---|---|"]
        for nm, m in (("lowest third", N <= q[0]), ("middle third", (N > q[0]) & (N <= q[1])), ("highest third", N > q[1])):
            if m.any():
                out.append(f"| {nm} | {int(m.sum())} | {np.median(N[m]):.3f} | {np.median(E[m]):.2f} |")
        rho = pd.Series(E).corr(pd.Series(Z), method="spearman")
        out.append(f"\nSpearman correlation of error and distance over all frames: {rho:+.2f} (distance also changes "
                   "the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--roots", nargs="*", default=[], help="session folders with room-* / run-* recordings (part 1)")
    ap.add_argument("--track", nargs="*", default=[], help="scr_anchor.py track output folders (part 2)")
    ap.add_argument("--near", type=float, default=950.0, help="mm: start of the Polaris volume along its axis")
    ap.add_argument("--far", type=float, default=2400.0, help="mm: end of the volume (3000 for the extended pyramid)")
    ap.add_argument("--bands", nargs="+", default=[850, 900, 950, 1100, 1500], help="mm: distance bands, part 2")
    ap.add_argument("--spike", type=float, default=1.0, help="mm: residual at the US image counted as a spike")
    ap.add_argument("--max-gap", type=float, default=0.08, help="s: longer gaps split the stream (as match_streams.py)")
    ap.add_argument("--window", type=float, default=1.0, help="s: smoothing of the tracked poses, part 2")
    ap.add_argument("--min-frames", type=int, default=30, help="part 2: frames inside the volume for a sweep to count")
    ap.add_argument("--calib", default=str(REPO / "calib_matrix.csv"), help="US calibration (TUS-REC format)")
    ap.add_argument("--out", default=None, help="also write the result to this .md")
    args = ap.parse_args()
    if not args.roots and not args.track:
        ap.error("give --roots and/or --track")
    P = us_points_marker(args.calib)
    md, warn = [f"# Polaris ground truth: volume {args.near:g}-{args.far:g} mm along the tracker axis", ""], []
    if args.roots:
        lines, warn = raw_check(args, P)
        md += ["## Raw tracker stream", ""] + lines
    if args.track:
        md += ["", "## Tracking error against the Polaris distance"] + track_check(args, P)
    md += ["", "## Warnings", ""] + ([f"- {w}" for w in warn] if warn else ["- none"])
    text = "\n".join(md) + "\n"
    print(text)
    if args.out:
        Path(args.out).write_text(text)
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
