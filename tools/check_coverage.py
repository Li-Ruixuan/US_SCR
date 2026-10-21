"""
Does the room scan cover the sweeps? Run on the recording PC right after recording, from the
raw pose.csv (Polaris) and the hand-eye only; no matching needed, takes seconds.

The anchor network only corrects over short distances (§6.3 of note_RPR.md): it needs a
room-scan view close to where the camera is during the sweep. A sweep frame counts as covered
if some room-scan frame was within --max-mm and --max-deg of its camera pose. Good room
scans (2XX, 3XX) cover 86-93 % of the sweep frames; the short 4XX room scans covered 0-14 %,
and anchoring failed there.

Workflow: room scan -> first sweep -> check -> if NO-GO, record another room scan over the
uncovered part (the printed time spans of the sweep show where) -> continue; check all
sweeps again at the end.

  python3 tools/check_coverage.py --root data/train_5XX --scans room-501 room-502
  python3 tools/check_coverage.py --root data/train_5XX --scans room-501 room-502 --sweeps run-501
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation

from match_streams import dedup_pose

ROOT = Path(__file__).resolve().parent.parent


def camera_poses(run_dir, T_marker_cam):
    """(timestamps, (N, 4, 4) T_world_cam) from the raw pose.csv, one per tracker measurement."""
    p = dedup_pose(pd.read_csv(run_dir / "pose.csv")).dropna()
    T = np.tile(np.eye(4), (len(p), 1, 1))
    T[:, :3, :3] = Rotation.from_quat(p[["qx", "qy", "qz", "qw"]].to_numpy()).as_matrix()
    T[:, :3, 3] = p[["tx", "ty", "tz"]].to_numpy()
    return p["timestamp"].to_numpy(float), T @ T_marker_cam


def spans(t, bad, min_s):
    """Time spans (s from the start) where bad is True for at least min_s."""
    out, i = [], 0
    while i < len(bad):
        if bad[i]:
            j = i
            while j < len(bad) and bad[j]:
                j += 1
            if t[j - 1] - t[i] >= min_s:
                out.append((t[i] - t[0], t[j - 1] - t[0]))
            i = j
        else:
            i += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="collection folder, e.g. data/train_5XX")
    ap.add_argument("--scans", nargs="+", required=True, help="room scans (the anchor map)")
    ap.add_argument("--sweeps", nargs="+", default=None, help="default: every run-* in --root")
    ap.add_argument("--hand-eye", default=str(ROOT / "T_marker_cam.npy"), help="T_marker_cam, mm")
    ap.add_argument("--max-mm", type=float, default=30.0)
    ap.add_argument("--max-deg", type=float, default=10.0)
    ap.add_argument("--min-covered", type=float, default=80.0, help="%% of sweep frames for GO")
    ap.add_argument("--min-gap-s", type=float, default=1.0, help="report uncovered spans of at least this")
    args = ap.parse_args()
    root = Path(args.root)
    T_mc = np.load(args.hand_eye)

    K = np.concatenate([camera_poses(root / s, T_mc)[1] for s in args.scans])
    sweeps = args.sweeps or sorted(p.name for p in root.iterdir() if p.name.startswith("run-") and (p / "pose.csv").exists())
    print(f"map: {' + '.join(args.scans)} ({len(K)} poses); covered = a room-scan pose within "
          f"{args.max_mm:g} mm and {args.max_deg:g} deg; GO at >= {args.min_covered:g} % of each sweep\n")
    n_go = 0
    for sw in sweeps:
        t, S = camera_poses(root / sw, T_mc)
        d = np.linalg.norm(S[:, None, :3, 3] - K[None, :, :3, 3], axis=2)
        tr = np.einsum("aij,bij->ab", S[:, :3, :3], K[:, :3, :3])
        ang = np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1)))
        ok = ((d < args.max_mm) & (ang < args.max_deg)).any(1)
        near = np.where(ang < args.max_deg, d, np.inf).min(1)            # nearest position at a similar angle
        pct = 100 * ok.mean()
        go = pct >= args.min_covered
        n_go += go
        gaps = spans(t, ~ok, args.min_gap_s)
        print(f"{sw}: {pct:3.0f} % covered, nearest similar view median {np.median(near[np.isfinite(near)]) if np.isfinite(near).any() else float('nan'):.0f} mm"
              f" -> {'GO' if go else 'NO-GO'}"
              + (f"; uncovered: " + ", ".join(f"{a:.0f}-{b:.0f} s" for a, b in gaps) if gaps and not go else ""))
    print(f"\n{n_go}/{len(sweeps)} sweeps covered." + ("" if n_go == len(sweeps) else
          " For NO-GO sweeps, scan the room again from the probe's positions and heights in the uncovered spans."))


if __name__ == "__main__":
    main()
