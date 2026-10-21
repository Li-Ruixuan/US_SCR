"""
One hand-eye (T_marker_cam) from several calibration sessions with the board NOT moved
between them, using still frames only.

Every still frame (marker angular speed < --stationary-deg-s) of every session gives
  T_world_board = T_world_marker . T_marker_cam . T_cam_board.
The board did not move, so one T_marker_cam and ONE T_world_board are fitted jointly
(robust least squares on the board's corner positions in mm). Still frames avoid the
camera/tracker timing offset and motion blur, which make moving frames disagree.

Printed: each session alone, the merged result, how far they are apart, and a
cross-check (fit on one session, residual on the other). Board detection is shared
with validate_hand_eye.py (board_poses.npz cache per run).

  python3 tools/merge_hand_eye.py --runs calib_201 calib_202 --out T_marker_cam_2XX.npy \
      --squares-x 12 --squares-y 9 --square-mm 15 --marker-mm 11.25 --dict DICT_5X5_1000
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from geometry import load_marker_poses                                   # noqa: E402
from validate_hand_eye import angular_velocity_deg_s, load_or_detect     # noqa: E402


def still_frames(run_dir, args):
    """(T_world_marker, T_cam_board) of the still frames with a board detection."""
    units = json.load(open(run_dir / "record_config.json")).get("pose", {}).get("units", "mm") \
        if (run_dir / "record_config.json").exists() else "mm"
    T_wm, _, df = load_marker_poses(run_dir / "frames.csv", units)
    idx, rvecs, tvecs, *_ = load_or_detect(run_dir, args)
    idx = np.asarray(idx, int)
    omega = angular_velocity_deg_s(T_wm, df.timestamp.to_numpy(np.float64), idx)
    keep = omega < args.stationary_deg_s
    T_cb = np.tile(np.eye(4), (len(idx), 1, 1))
    for k in range(len(idx)):
        T_cb[k, :3, :3] = cv2.Rodrigues(np.asarray(rvecs[k], float))[0]
        T_cb[k, :3, 3] = np.asarray(tvecs[k], float).ravel()
    print(f"  {run_dir.name}: {len(idx)} frames with the board, {keep.sum()} still "
          f"(< {args.stationary_deg_s:g} deg/s)")
    return T_wm[idx][keep], T_cb[keep]


def to_T(p):
    T = np.eye(4)
    T[:3, :3] = Rotation.from_rotvec(p[:3]).as_matrix()
    T[:3, 3] = p[3:]
    return T


def to_p(T):
    return np.r_[Rotation.from_matrix(T[:3, :3]).as_rotvec(), T[:3, 3]]


def fit(T_wm, T_cb, C, X0):
    """Joint fit of T_marker_cam (X) and the fixed board pose T_world_board (W)."""
    W0 = T_wm[0] @ X0 @ T_cb[0]

    def res(p):
        X, W = to_T(p[:6]), to_T(p[6:])
        return ((T_wm @ X @ T_cb @ C)[:, :3] - (W @ C)[None, :3]).ravel()

    r = least_squares(res, np.r_[to_p(X0), to_p(W0)], loss="huber", f_scale=5.0)
    return to_T(r.x[:6]), to_T(r.x[6:])


def corner_error(X, W, T_wm, T_cb, C):
    """Median distance (mm) between where each frame puts the board corners and W."""
    return float(np.median(np.linalg.norm((T_wm @ X @ T_cb @ C)[:, :3] - (W @ C)[None, :3], axis=1)))


def rot_deg(A, B):
    return float(np.degrees(Rotation.from_matrix(A[:3, :3].T @ B[:3, :3]).magnitude()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/calib")
    ap.add_argument("--runs", nargs="+", required=True, help="sessions with the board in the same place")
    ap.add_argument("--out", default=None, help="save the merged T_marker_cam (.npy, mm)")
    ap.add_argument("--init", default="T_marker_cam.npy", help="starting guess")
    ap.add_argument("--squares-x", type=int, default=12)
    ap.add_argument("--squares-y", type=int, default=9)
    ap.add_argument("--square-mm", type=float, default=15.0)
    ap.add_argument("--marker-mm", type=float, default=11.25)
    ap.add_argument("--dict", default="DICT_5X5_1000")
    ap.add_argument("--min-corners", type=int, default=12)
    ap.add_argument("--max-reproj-error", type=float, default=1.0)
    ap.add_argument("--stationary-deg-s", type=float, default=5.0)
    ap.add_argument("--no-cache", action="store_true", help="redetect the board")
    args = ap.parse_args()

    s = args.square_mm                       # outer ChArUco corners of the board, in its own frame
    a, b = s, (args.squares_x - 1) * s
    c, d = s, (args.squares_y - 1) * s
    C = np.array([[a, c, 0, 1], [b, c, 0, 1], [b, d, 0, 1], [a, d, 0, 1]], float).T

    sets = {r: still_frames(Path(args.root) / r, args) for r in args.runs}
    X0 = np.load(args.init) if Path(args.init).exists() else np.eye(4)
    T_wm = np.concatenate([v[0] for v in sets.values()])
    T_cb = np.concatenate([v[1] for v in sets.values()])
    XM, WM = fit(T_wm, T_cb, C, X0)

    np.set_printoptions(precision=6, suppress=True)
    print("\nper session vs merged (still frames):")
    single = {}
    for r, (a_wm, a_cb) in sets.items():
        X, W = fit(a_wm, a_cb, C, XM)
        single[r] = (X, W)
        print(f"  {r:10s} t = {np.round(X[:3, 3], 1)} | lever {np.linalg.norm(X[:3, 3]):.1f} mm | "
              f"vs merged {np.linalg.norm(X[:3, 3] - XM[:3, 3]):.1f} mm, {rot_deg(X, XM):.2f} deg | "
              f"own corner error {corner_error(X, W, a_wm, a_cb, C):.1f} mm")
    print(f"  MERGED     t = {np.round(XM[:3, 3], 1)} | lever {np.linalg.norm(XM[:3, 3]):.1f} mm | "
          f"corner error {corner_error(XM, WM, T_wm, T_cb, C):.1f} mm")
    runs = list(sets)
    if len(runs) > 1:
        (Xa, Wa), (Xb, Wb) = single[runs[0]], single[runs[1]]
        print(f"  board pose {runs[0]} vs {runs[1]}: {np.linalg.norm(Wa[:3, 3] - Wb[:3, 3]):.1f} mm, "
              f"{rot_deg(Wa, Wb):.2f} deg (about 0 if the board did not move)")
        print(f"  cross-check, fit one / test the other: {runs[0]} -> {runs[1]} "
              f"{corner_error(Xa, Wa, *sets[runs[1]], C):.1f} mm, {runs[1]} -> {runs[0]} "
              f"{corner_error(Xb, Wb, *sets[runs[0]], C):.1f} mm")
    if Path(args.init).exists():
        print(f"  vs {args.init}: {np.linalg.norm(X0[:3, 3] - XM[:3, 3]):.1f} mm, {rot_deg(X0, XM):.2f} deg")
    print("\nmerged T_marker_cam (mm):\n", XM)
    if args.out:
        np.save(args.out, XM)
        print(f"saved {args.out}")


if __name__ == "__main__":
    main()
