"""
Validate a hand-eye solution across one or more ChArUco calibration sessions.

What it answers, in order:

  1. Is the translation poorly conditioned?   -> method spread within a session
  2. Is the residual caused by motion?        -> residual vs angular velocity
  3. Is there a camera/tracker timing offset? -> time-offset sweep
  4. Does a stationary-only subset fix it?    -> re-solve on still frames
  5. Does the solution generalise?            -> held-out reprojection, in px
  6. Do independent sessions agree?           -> cross-session comparison

Sessions may have the board in different places -- T_marker_cam does not
involve the board, so each session estimates its own T_world_target
independently and the results are directly comparable. The board must be
fixed *within* each session.

Usage:
  python3 tools/validate_hand_eye.py --self-test
  python3 tools/validate_hand_eye.py --root data/calib --runs calib_001 calib_003
  python3 tools/validate_hand_eye.py --root data/calib --runs calib_001 \
      --time-offset-sweep --stationary-deg-s 3.0

Board detection is cached per run in board_poses.npz; delete it or pass
--no-cache to redetect.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import cv2
import cv2.aruco as aruco
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from geometry import load_intrinsics, load_marker_poses  # noqa: E402
from calibrate_hand_eye import (HAND_EYE_METHODS, detect_board_pose,  # noqa: E402
                                solve_hand_eye)

__all__ = ["rotation_angle_deg", "chordal_mean_rotation", "angular_velocity_deg_s",
           "implied_world_target", "residuals_about_mean", "shift_poses_in_time"]


# ---------------------------------------------------------------------------
# SE(3) helpers
# ---------------------------------------------------------------------------

def rotation_angle_deg(R: np.ndarray) -> float:
    """Geodesic angle of a rotation matrix, in degrees."""
    cos = np.clip((np.trace(R) - 1.0) * 0.5, -1.0, 1.0)
    return float(np.degrees(np.arccos(cos)))


def rotation_diff_deg(Ra: np.ndarray, Rb: np.ndarray) -> float:
    return rotation_angle_deg(Ra.T @ Rb)


def chordal_mean_rotation(Rs: np.ndarray) -> np.ndarray:
    """Chordal (L2) mean of a stack of rotation matrices, (N, 3, 3) -> (3, 3).

    Sum, then project back onto SO(3) via SVD. The determinant correction is
    not optional: without it the projection can return a reflection, which
    fits marginally better and is not a rotation -- the same failure
    solver.kabsch guards against.
    """
    S = np.sum(Rs, axis=0)
    if not np.all(np.isfinite(S)):
        return np.full((3, 3), np.nan)
    U, _, Vt = np.linalg.svd(S)
    d = np.sign(np.linalg.det(U @ Vt))
    return U @ np.diag([1.0, 1.0, d]) @ Vt


def valid_solution(T) -> bool:
    """Is this a usable rigid transform?

    cv2.calibrateHandEye does not raise on a degenerate problem -- it logs to
    stderr and returns a zero or garbage matrix. Downstream that becomes a
    silent NaN, so every solution is checked here before use.
    """
    if T is None or not np.all(np.isfinite(T)):
        return False
    R = T[:3, :3]
    if np.linalg.norm(R) < 1e-9:
        return False
    if not np.allclose(R.T @ R, np.eye(3), atol=1e-4):
        return False
    return abs(np.linalg.det(R) - 1.0) < 1e-4


def slerp_matrix(Ra: np.ndarray, Rb: np.ndarray, u: float) -> np.ndarray:
    """Interpolate between two rotation matrices along the geodesic."""
    Rel = Ra.T @ Rb
    theta = np.radians(rotation_angle_deg(Rel))
    if theta < 1e-9:
        return Ra.copy()
    axis = np.array([Rel[2, 1] - Rel[1, 2],
                     Rel[0, 2] - Rel[2, 0],
                     Rel[1, 0] - Rel[0, 1]])
    n = np.linalg.norm(axis)
    if n < 1e-12:
        return Ra.copy()
    rvec = (axis / n) * (theta * u)
    R_step, _ = cv2.Rodrigues(rvec)
    return Ra @ R_step


# ---------------------------------------------------------------------------
# Motion
# ---------------------------------------------------------------------------

def angular_velocity_deg_s(T_world_marker: np.ndarray, stamps: np.ndarray,
                           idx: np.ndarray) -> np.ndarray:
    """Marker angular speed at each frame in idx, by central difference.

    Motion is the common cause of the three error sources this tool separates:
    a camera/tracker timing offset turns angular speed directly into pose
    error, motion blur biases corner detection, and both correlate with speed
    while static geometry errors do not.
    """
    out = np.zeros(len(idx))
    for k, i in enumerate(idx):
        lo = idx[max(k - 1, 0)]
        hi = idx[min(k + 1, len(idx) - 1)]
        dt = stamps[hi] - stamps[lo]
        if dt <= 1e-6:
            out[k] = np.inf
            continue
        ang = rotation_diff_deg(T_world_marker[lo, :3, :3], T_world_marker[hi, :3, :3])
        out[k] = ang / dt
    return out


def shift_poses_in_time(T_world_marker: np.ndarray, stamps: np.ndarray,
                        idx: np.ndarray, tau: float):
    """Tracker poses re-sampled at stamps[idx] + tau.

    Interpolates between the per-frame poses already in frames.csv (slerp on
    rotation, linear on translation). Those are themselves interpolations of
    the 60 Hz stream, so this is only valid for |tau| of a frame or two --
    enough to locate a latency of a few tens of milliseconds, which is the
    scale that matters here.

    Returns (T_shifted, ok) where ok marks frames whose shifted time still
    falls inside the recording.
    """
    T_out = np.zeros((len(idx), 4, 4))
    ok = np.zeros(len(idx), dtype=bool)
    order = np.argsort(stamps)
    s_sorted = stamps[order]

    for k, i in enumerate(idx):
        t = stamps[i] + tau
        if t < s_sorted[0] or t > s_sorted[-1]:
            continue
        j = int(np.searchsorted(s_sorted, t))
        j = int(np.clip(j, 1, len(s_sorted) - 1))
        a, b = order[j - 1], order[j]
        t0, t1 = stamps[a], stamps[b]
        u = 0.0 if t1 <= t0 else (t - t0) / (t1 - t0)
        T = np.eye(4)
        T[:3, :3] = slerp_matrix(T_world_marker[a, :3, :3],
                                 T_world_marker[b, :3, :3], u)
        T[:3, 3] = T_world_marker[a, :3, 3] + u * (
            T_world_marker[b, :3, 3] - T_world_marker[a, :3, 3])
        T_out[k] = T
        ok[k] = True
    return T_out, ok


# ---------------------------------------------------------------------------
# Residuals
# ---------------------------------------------------------------------------

def implied_world_target(T_world_marker: np.ndarray, T_marker_cam: np.ndarray,
                         T_cam_target: np.ndarray) -> np.ndarray:
    """Per-frame T_world_target implied by a candidate hand-eye transform.

    The board is fixed, so every frame must imply the same transform. All
    disagreement is error somewhere in the chain.
    """
    return np.einsum("nij,jk,nkl->nil", T_world_marker, T_marker_cam, T_cam_target)


def residuals_about_mean(T_implied: np.ndarray):
    """(translation mm, rotation deg) of each frame from the mean T_world_target.

    Deviation from the mean rather than random pairwise differences: it gives
    one residual per frame, which can then be correlated against that frame's
    angular velocity. A pairwise residual cannot be attributed to a frame.
    """
    t_mean = T_implied[:, :3, 3].mean(axis=0)
    R_mean = chordal_mean_rotation(T_implied[:, :3, :3])
    d_t = np.linalg.norm(T_implied[:, :3, 3] - t_mean, axis=1)
    d_r = np.array([rotation_diff_deg(R_mean, T[:3, :3]) for T in T_implied])
    return d_t, d_r


# ---------------------------------------------------------------------------
# Detection, with cache
# ---------------------------------------------------------------------------

def load_or_detect(run_dir: Path, args):
    """Board pose per usable frame. Cached: detection dominates runtime."""
    cache = run_dir / "board_poses.npz"
    if cache.exists() and not args.no_cache:
        d = np.load(cache, allow_pickle=True)
        if int(d["min_corners"]) == args.min_corners:
            print(f"  using cached detections ({len(d['idx'])} frames) "
                  f"-- --no-cache to redetect")
            return (d["idx"], d["rvec"], d["tvec"], d["err"],
                    list(d["obj"]), list(d["img"]))
        print("  cache was built with a different --min-corners; redetecting")

    cfg_path = run_dir / "record_config.json"
    pose_units = "mm"
    if cfg_path.exists():
        pose_units = json.load(open(cfg_path)).get("pose", {}).get("units", "mm")

    _, valid, df = load_marker_poses(run_dir / "frames.csv", pose_units)
    K, _ = load_intrinsics(run_dir / "camera_info.json")
    D = np.array(json.load(open(run_dir / "camera_info.json"))["D"], dtype=np.float64)

    dictionary = aruco.getPredefinedDictionary(getattr(aruco, args.dict))
    board = aruco.CharucoBoard((args.squares_x, args.squares_y),
                               args.square_mm, args.marker_mm, dictionary)
    detector = aruco.CharucoDetector(board, aruco.CharucoParameters(),
                                     aruco.DetectorParameters())

    idx, rvecs, tvecs, errs, objs, imgs = [], [], [], [], [], []
    n_seen = n_few = n_reproj = 0
    for i in np.flatnonzero(valid):
        p = run_dir / df.rgb.iloc[i]
        gray = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if gray is None:
            continue
        n_seen += 1

        res = detector.detectBoard(gray)
        charuco_corners, charuco_ids = res[0], res[1]
        if charuco_ids is None or len(charuco_ids) < args.min_corners:
            n_few += 1
            continue
        obj_pts, img_pts = board.matchImagePoints(charuco_corners, charuco_ids)
        if obj_pts is None or len(obj_pts) < args.min_corners:
            n_few += 1
            continue

        det = detect_board_pose(gray, board, detector, K, D, args.min_corners)
        if det is None:
            n_few += 1
            continue
        R, t, err, _ = det
        if err > args.max_reproj_error:
            n_reproj += 1
            continue

        rvec, _ = cv2.Rodrigues(R)
        idx.append(int(i))
        rvecs.append(rvec.ravel())
        tvecs.append(np.asarray(t).ravel())
        errs.append(float(err))
        objs.append(np.asarray(obj_pts, dtype=np.float64).reshape(-1, 3))
        imgs.append(np.asarray(img_pts, dtype=np.float64).reshape(-1, 2))

    print(f"  {n_seen} frames with a tracker pose; {len(idx)} usable "
          f"({n_few} rejected: fewer than {args.min_corners} corners; "
          f"{n_reproj} rejected: reprojection error above {args.max_reproj_error}px)")

    idx = np.array(idx, dtype=int)
    np.savez(cache, idx=idx, rvec=np.array(rvecs), tvec=np.array(tvecs),
             err=np.array(errs), obj=np.array(objs, dtype=object),
             img=np.array(imgs, dtype=object), min_corners=args.min_corners,
             allow_pickle=True)
    return idx, np.array(rvecs), np.array(tvecs), np.array(errs), objs, imgs


# ---------------------------------------------------------------------------
# Per-run analysis
# ---------------------------------------------------------------------------

def solve_all_methods(T_wm, T_ct):
    """Every OpenCV method on the same data.

    Agreement across methods is the conditioning test. A well-constrained
    problem gives near-identical answers; a spread of tens of millimetres
    means the solvers are each picking a different point from a nearly flat
    cost valley, and no single one of them is trustworthy.
    """
    R_g2b = [T[:3, :3] for T in T_wm]
    t_g2b = [T[:3, 3] for T in T_wm]
    R_t2c = [T[:3, :3] for T in T_ct]
    t_t2c = [T[:3, 3] for T in T_ct]
    out = {}
    for name in HAND_EYE_METHODS:
        try:
            T = solve_hand_eye(R_g2b, t_g2b, R_t2c, t_t2c, name)
        except cv2.error:
            T = None
        out[name] = T if valid_solution(T) else None
    return out


def method_spread(solutions: dict):
    """Max pairwise disagreement over the methods that returned something."""
    Ts = [T for T in solutions.values() if T is not None]
    if len(Ts) < 2:
        return float("nan"), float("nan"), []
    levers = [float(np.linalg.norm(T[:3, 3])) for T in Ts]
    dt = max(np.linalg.norm(a[:3, 3] - b[:3, 3])
             for a in Ts for b in Ts)
    dr = max(rotation_diff_deg(a[:3, :3], b[:3, :3]) for a in Ts for b in Ts)
    return float(dt), float(dr), levers


def print_method_table(solutions: dict, label: str):
    print(f"\n  {label}")
    print(f"  {'method':12s} {'lever_mm':>9s} {'tx':>9s} {'ty':>9s} {'tz':>9s}")
    for name, T in solutions.items():
        if T is None:
            print(f"  {name:12s} {'FAILED':>9s}   (degenerate or not a rotation)")
            continue
        tx, ty, tz = T[:3, 3]
        print(f"  {name:12s} {np.linalg.norm(T[:3,3]):9.1f} "
              f"{tx:9.1f} {ty:9.1f} {tz:9.1f}")


def residual_vs_velocity(d_t, d_r, omega, n_bins=4):
    """Bin residuals by angular speed.

    This is the fingerprint that separates the error sources. A timing offset
    between camera and tracker turns angular speed straight into pose error,
    and motion blur biases corners in a way that correlates with speed too.
    Static geometry error -- a small board, a weak planar pose, too few
    rotations -- does not care how fast the probe was moving. So a residual
    that climbs with speed points at timing or blur, and a flat one points at
    geometry.
    """
    finite = np.isfinite(omega)
    if finite.sum() < n_bins * 4:
        return None
    o, dt, dr = omega[finite], d_t[finite], d_r[finite]
    edges = np.quantile(o, np.linspace(0, 1, n_bins + 1))
    rows = []
    for b in range(n_bins):
        m = (o >= edges[b]) & (o <= edges[b + 1] if b == n_bins - 1 else o < edges[b + 1])
        if m.sum() < 2:
            continue
        rows.append({"omega_lo": float(edges[b]), "omega_hi": float(edges[b + 1]),
                     "n": int(m.sum()),
                     "trans_mm": float(np.median(dt[m])),
                     "rot_deg": float(np.median(dr[m]))})
    if len(rows) < 2:
        return None
    ratio_t = rows[-1]["trans_mm"] / max(rows[0]["trans_mm"], 1e-9)
    ratio_r = rows[-1]["rot_deg"] / max(rows[0]["rot_deg"], 1e-9)
    return {"bins": rows, "fastest_over_slowest_trans": float(ratio_t),
            "fastest_over_slowest_rot": float(ratio_r)}


def heldout_reprojection(T_wm, T_ct, T_marker_cam, objs, imgs, K, D):
    """Fit T_world_target on the first half, reproject on the second, in pixels.

    Two reasons this is the strongest single number here. It is held out, so
    it cannot be satisfied by overfitting the frames the hand-eye was solved
    from -- unlike the AX=XB residual, which is a fit statistic. And it is
    measured in the units the corner detection is actually accurate in, so
    sub-pixel versus tens of pixels is unambiguous.

    Split is by contiguous halves, not at random: consecutive frames are
    near-duplicates, and a random split would put near-identical frames on
    both sides and leak.
    """
    n = len(T_wm)
    if n < 20:
        return None
    half = n // 2

    T_imp = implied_world_target(T_wm[:half], T_marker_cam, T_ct[:half])
    T_target = np.eye(4)
    T_target[:3, :3] = chordal_mean_rotation(T_imp[:, :3, :3])
    T_target[:3, 3] = T_imp[:, :3, 3].mean(axis=0)

    errs = []
    for k in range(half, n):
        T_cam_world = np.linalg.inv(T_wm[k] @ T_marker_cam)
        T_pred = T_cam_world @ T_target
        rvec, _ = cv2.Rodrigues(T_pred[:3, :3])
        # Elements read back from the npz cache carry object dtype, which
        # projectPoints rejects; cast explicitly rather than relying on it.
        obj = np.asarray(objs[k], dtype=np.float64).reshape(-1, 1, 3)
        img = np.asarray(imgs[k], dtype=np.float64).reshape(-1, 2)
        proj, _ = cv2.projectPoints(obj, rvec,
                                    T_pred[:3, 3].reshape(3, 1), K, D)
        errs.append(float(np.linalg.norm(
            proj.reshape(-1, 2) - img, axis=1).mean()))
    errs = np.array(errs)
    return {"n_fit": half, "n_test": len(errs),
            "median_px": float(np.median(errs)),
            "p90_px": float(np.percentile(errs, 90)),
            "max_px": float(errs.max())}


def time_offset_sweep(T_world_marker, stamps, idx, T_ct, method, taus):
    """Re-solve at a range of camera-minus-tracker timing offsets.

    The pose in frames.csv is interpolated onto the camera stamp. Any constant
    latency between exposure and tracker stamp becomes a pose error
    proportional to angular speed -- at 50 deg/s a 10 ms offset is 0.5 deg.
    If the residual has a clear minimum away from zero, that offset is real
    and worth correcting at the recorder rather than in the solver.
    """
    rows = []
    for tau in taus:
        T_shift, ok = shift_poses_in_time(T_world_marker, stamps, idx, tau)
        if ok.sum() < 20:
            continue
        T_wm_s, T_ct_s = T_shift[ok], T_ct[ok]
        try:
            T_he = solve_all_methods(T_wm_s, T_ct_s)[method]
        except cv2.error:
            continue
        if T_he is None:
            continue
        d_t, d_r = residuals_about_mean(
            implied_world_target(T_wm_s, T_he, T_ct_s))
        rows.append({"tau_ms": float(tau * 1e3), "n": int(ok.sum()),
                     "trans_mm": float(np.median(d_t)),
                     "rot_deg": float(np.median(d_r)),
                     "lever_mm": float(np.linalg.norm(T_he[:3, 3]))})
    return rows


def analyse_run(run: str, args) -> dict:
    run_dir = Path(args.root) / run
    print(f"\n{'=' * 70}\n{run}\n{'=' * 70}")

    cfg_path = run_dir / "record_config.json"
    pose_units = "mm"
    if cfg_path.exists():
        pose_units = json.load(open(cfg_path)).get("pose", {}).get("units", "mm")
    T_world_marker, valid, df = load_marker_poses(run_dir / "frames.csv", pose_units)
    K, _ = load_intrinsics(run_dir / "camera_info.json")
    D = np.array(json.load(open(run_dir / "camera_info.json"))["D"], dtype=np.float64)
    stamps = df.timestamp.to_numpy(dtype=np.float64)

    idx, rvecs, tvecs, errs, objs, imgs = load_or_detect(run_dir, args)
    if len(idx) < 20:
        print("  too few usable frames to say anything. Stopping.")
        return {"run": run, "usable_frames": int(len(idx))}

    T_ct = np.zeros((len(idx), 4, 4))
    for k in range(len(idx)):
        R, _ = cv2.Rodrigues(rvecs[k])
        T_ct[k] = np.eye(4)
        T_ct[k][:3, :3] = R
        T_ct[k][:3, 3] = tvecs[k]
    T_wm = T_world_marker[idx]

    omega = angular_velocity_deg_s(T_world_marker, stamps, idx)
    spread = np.array([rotation_diff_deg(T_wm[0, :3, :3], T[:3, :3]) for T in T_wm])
    print(f"  orientation spread from first frame: median {np.median(spread):.1f} "
          f"deg, p90 {np.percentile(spread, 90):.1f}, max {spread.max():.1f}")
    print(f"  angular speed: median {np.median(omega[np.isfinite(omega)]):.1f} deg/s, "
          f"p90 {np.percentile(omega[np.isfinite(omega)], 90):.1f} deg/s")
    print(f"  board reprojection (solvePnP fit): median {np.median(errs):.2f} px")

    result = {"run": run, "usable_frames": int(len(idx)),
              "orientation_spread_deg": {
                  "median": float(np.median(spread)),
                  "p90": float(np.percentile(spread, 90)),
                  "max": float(spread.max())}}

    # --- all frames -------------------------------------------------------
    sol_all = solve_all_methods(T_wm, T_ct)
    print_method_table(sol_all, "ALL frames")
    dt_s, dr_s, levers = method_spread(sol_all)
    print(f"  method spread: {dt_s:.1f} mm translation, {dr_s:.2f} deg rotation")
    result["all_frames"] = {
        "n": int(len(idx)),
        "method_spread_mm": dt_s, "method_spread_deg": dr_s,
        "levers_mm": levers,
        "solutions": {k: (None if v is None else v.tolist())
                      for k, v in sol_all.items()}}

    T_chosen = sol_all[args.method]
    if T_chosen is None:
        print(f"  --method {args.method} failed on this run.")
        return result

    d_t, d_r = residuals_about_mean(implied_world_target(T_wm, T_chosen, T_ct))
    print(f"\n  residual about the mean T_world_target ({args.method}, all frames):")
    print(f"    translation median {np.median(d_t):6.2f} mm  p90 {np.percentile(d_t,90):6.2f}")
    print(f"    rotation    median {np.median(d_r):6.2f} deg p90 {np.percentile(d_r,90):6.2f}")
    result["all_frames"]["residual"] = {
        "trans_mm_median": float(np.median(d_t)),
        "rot_deg_median": float(np.median(d_r))}

    # --- residual vs angular velocity -------------------------------------
    rv = residual_vs_velocity(d_t, d_r, omega, args.velocity_bins)
    if rv:
        print("\n  residual vs angular speed (the timing/blur fingerprint):")
        print(f"    {'speed deg/s':>16s} {'n':>5s} {'trans mm':>9s} {'rot deg':>8s}")
        for b in rv["bins"]:
            print(f"    {b['omega_lo']:7.1f}-{b['omega_hi']:6.1f} {b['n']:5d} "
                  f"{b['trans_mm']:9.2f} {b['rot_deg']:8.2f}")
        print(f"    fastest/slowest bin: {rv['fastest_over_slowest_rot']:.2f}x rotation, "
              f"{rv['fastest_over_slowest_trans']:.2f}x translation")
        speed_ratio = rv["bins"][-1]["omega_hi"] / max(rv["bins"][0]["omega_lo"], 1e-9)
        if speed_ratio < 3.0:
            # Same trap as measuring a hand-eye error between two nearly
            # identical viewpoints: if the probe moved at one speed all
            # session, a speed-dependent error cannot show up as a difference
            # between bins, and a flat result means nothing.
            print(f"    NOTE: speed varied by only {speed_ratio:.1f}x across "
                  "the session, so this test has little leverage. A flat "
                  "result here is not evidence against a timing offset -- use "
                  "the offset sweep instead.")
        elif rv["fastest_over_slowest_rot"] > 1.5:
            print("    -> residual climbs with speed: timing offset or motion "
                  "blur, not board geometry")
        else:
            print("    -> residual is flat in speed: the cause is geometry "
                  "(board size, distance, rotation coverage), not motion")
        result["residual_vs_velocity"] = rv

    # --- stationary subset ------------------------------------------------
    still = np.isfinite(omega) & (omega < args.stationary_deg_s)
    print(f"\n  stationary frames (< {args.stationary_deg_s} deg/s): "
          f"{still.sum()}/{len(idx)}")
    still_spread = 0.0
    if still.sum() >= 2:
        T_still_wm = T_wm[still]
        still_spread = max(rotation_diff_deg(T_still_wm[0, :3, :3], T[:3, :3])
                           for T in T_still_wm)
        print(f"  their orientation spread: {still_spread:.1f} deg")
    # Filtering out motion is only useful if the probe visited many DIFFERENT
    # static poses. Still frames clustered at one pose have no relative motion
    # at all, and hand-eye is unsolvable from them -- OpenCV returns zeros
    # rather than raising, so this has to be caught here.
    if still.sum() >= args.min_stationary and still_spread < 30.0:
        print("  -> all clustered at one orientation, so there is no relative "
              "motion to solve from. A stationary subset only helps if the "
              "session paused at many different poses.")
    elif still.sum() >= args.min_stationary:
        sol_still = solve_all_methods(T_wm[still], T_ct[still])
        print_method_table(sol_still, f"STATIONARY frames ({still.sum()})")
        dt_ss, dr_ss, levers_ss = method_spread(sol_still)
        print(f"  method spread: {dt_ss:.1f} mm translation, {dr_ss:.2f} deg rotation")
        T_still = sol_still[args.method]
        entry = {"n": int(still.sum()), "method_spread_mm": dt_ss,
                 "method_spread_deg": dr_ss, "levers_mm": levers_ss}
        if T_still is not None:
            d_t2, d_r2 = residuals_about_mean(
                implied_world_target(T_wm[still], T_still, T_ct[still]))
            print(f"  residual: translation median {np.median(d_t2):.2f} mm, "
                  f"rotation median {np.median(d_r2):.2f} deg")
            print(f"  vs all frames: lever {np.linalg.norm(T_chosen[:3,3]):.1f} -> "
                  f"{np.linalg.norm(T_still[:3,3]):.1f} mm, rotation moved "
                  f"{rotation_diff_deg(T_chosen[:3,:3], T_still[:3,:3]):.3f} deg")
            entry["solution"] = T_still.tolist()
            entry["residual"] = {"trans_mm_median": float(np.median(d_t2)),
                                 "rot_deg_median": float(np.median(d_r2))}
            if dt_ss < 0.5 * dt_s:
                print("  -> the spread collapses on still frames. Motion is the "
                      "cause; re-record with discrete static poses.")
        result["stationary"] = entry
    else:
        print(f"  too few to re-solve (need {args.min_stationary}). The session "
              "was a continuous sweep with no pauses.")

    # --- held-out reprojection -------------------------------------------
    rep = heldout_reprojection(T_wm, T_ct, T_chosen, objs, imgs, K, D)
    if rep:
        print(f"\n  held-out reprojection (fit on {rep['n_fit']}, test on "
              f"{rep['n_test']} frames):")
        print(f"    median {rep['median_px']:.2f} px  p90 {rep['p90_px']:.2f}  "
              f"max {rep['max_px']:.2f}")
        if rep["median_px"] < 2.0:
            print("    -> consistent with the images on frames it never saw")
        elif rep["median_px"] < 10.0:
            print("    -> a real residual error, well above detection noise")
        else:
            print("    -> does not generalise. Do not train on this.")
        result["heldout_reprojection"] = rep

    # --- time offset ------------------------------------------------------
    if args.time_offset_sweep:
        taus = np.arange(-args.tau_max_ms, args.tau_max_ms + 1e-9,
                         args.tau_step_ms) * 1e-3
        rows = time_offset_sweep(T_world_marker, stamps, idx, T_ct,
                                 args.method, taus)
        if rows:
            # Judge on the translation residual, not rotation. Rotation is
            # swamped by solvePnP's own out-of-plane noise on a small planar
            # board, so a real latency can move translation by tens of percent
            # while barely touching rotation.
            best = min(rows, key=lambda r: r["trans_mm"])
            zero = min(rows, key=lambda r: abs(r["tau_ms"]))
            print(f"\n  timing offset sweep ({args.method}):")
            print(f"    {'tau ms':>8s} {'rot deg':>8s} {'trans mm':>9s} {'lever mm':>9s}")
            for r in rows:
                mark = "  <-- best" if r is best else ""
                print(f"    {r['tau_ms']:8.1f} {r['rot_deg']:8.2f} "
                      f"{r['trans_mm']:9.2f} {r['lever_mm']:9.1f}{mark}")
            gain = 1.0 - best["trans_mm"] / max(zero["trans_mm"], 1e-9)
            gain_r = 1.0 - best["rot_deg"] / max(zero["rot_deg"], 1e-9)
            if abs(best["tau_ms"]) >= args.tau_step_ms and gain > 0.15:
                print(f"    -> translation residual minimises at "
                      f"{best['tau_ms']:.0f} ms, {100*gain:.0f}% below tau=0 "
                      f"(rotation {100*gain_r:+.0f}%). A real latency between "
                      "camera and tracker stamps; fix it at the recorder "
                      "rather than compensating in the solver.")
                if best["tau_ms"] in (rows[0]["tau_ms"], rows[-1]["tau_ms"]):
                    print("       the minimum sits at the edge of the sweep -- "
                          "widen --tau-max-ms, the true offset may be larger")
            else:
                print("    -> no clear minimum away from zero; timing is not "
                      "the dominant error")
            result["time_offset_sweep"] = rows
    return result


# ---------------------------------------------------------------------------
# Cross-session comparison
# ---------------------------------------------------------------------------

def compare_sessions(results: list, args) -> dict:
    """Two sessions are two independent experiments.

    With the board in a different place each time, a systematic error tied to
    one placement -- a distortion artefact at one part of the image, a bias at
    one working distance -- cannot reproduce. Agreement is therefore much
    stronger evidence than any within-session residual, which is a fit
    statistic.

    Rotation and translation are reported separately on purpose: rotation is
    well determined by modest motion, translation only by large rotations, so
    they routinely disagree in quality and a single combined number would
    hide that.
    """
    usable = [(r["run"], np.array(r["all_frames"]["solutions"][args.method]))
              for r in results
              if r.get("all_frames", {}).get("solutions", {}).get(args.method)]
    if len(usable) < 2:
        return {}

    print(f"\n{'=' * 70}\ncross-session agreement ({args.method})\n{'=' * 70}")
    out = []
    for i in range(len(usable)):
        for j in range(i + 1, len(usable)):
            (na, Ta), (nb, Tb) = usable[i], usable[j]
            d_t = float(np.linalg.norm(Ta[:3, 3] - Tb[:3, 3]))
            d_r = rotation_diff_deg(Ta[:3, :3], Tb[:3, :3])
            lever = 0.5 * (np.linalg.norm(Ta[:3, 3]) + np.linalg.norm(Tb[:3, 3]))
            implied = lever * np.radians(d_r)
            print(f"  {na} vs {nb}:")
            print(f"    rotation    {d_r:.3f} deg  -> {implied:.2f} mm at a "
                  f"{lever:.0f} mm lever arm")
            print(f"    translation {d_t:.2f} mm")
            if d_r < 0.5:
                print("    rotation agrees. This is the half that dominates the "
                      "error budget, and it is settled.")
            else:
                print("    rotation disagrees by more than half a degree -- more "
                      "than the whole budget at this lever arm.")
            if d_t < 2.0:
                print("    translation agrees.")
            else:
                print("    translation does not agree. It is observable only "
                      "through large rotations; treat the lever arm as "
                      "uncertain by about this much.")
            out.append({"a": na, "b": nb, "rotation_deg": d_r,
                        "translation_mm": d_t,
                        "implied_displacement_mm": float(implied)})
    return {"pairs": out}


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test():
    """Verify the helpers on data with a known answer, before real use."""
    rng = np.random.default_rng(0)

    R = cv2.Rodrigues(np.array([0.3, -0.2, 0.8]))[0]
    assert abs(rotation_diff_deg(R, R)) < 1e-9
    assert abs(rotation_angle_deg(np.eye(3))) < 1e-9

    Rs = np.stack([cv2.Rodrigues(rng.normal(scale=0.02, size=3) +
                                 np.array([0.3, -0.2, 0.8]))[0] for _ in range(200)])
    M = chordal_mean_rotation(Rs)
    assert abs(np.linalg.det(M) - 1.0) < 1e-9, "chordal mean is not a rotation"
    assert rotation_diff_deg(M, R) < 1.0, "chordal mean is far from the truth"

    Ra = np.eye(3)
    Rb = cv2.Rodrigues(np.array([0.0, 0.0, np.radians(90.0)]))[0]
    assert abs(rotation_angle_deg(Ra.T @ slerp_matrix(Ra, Rb, 0.5)) - 45.0) < 1e-6

    # A planted hand-eye must give exactly zero residual.
    T_he = np.eye(4)
    T_he[:3, :3] = cv2.Rodrigues(np.array([0.6, -0.4, 0.9]))[0]
    T_he[:3, 3] = [80.0, -35.0, 45.0]
    T_target = np.eye(4)
    T_target[:3, :3] = cv2.Rodrigues(np.array([0.1, 0.2, -0.15]))[0]
    T_target[:3, 3] = [150.0, 300.0, 2200.0]

    T_wm, T_ct = [], []
    for _ in range(40):
        T = np.eye(4)
        phi = rng.normal(size=3)
        T[:3, :3] = cv2.Rodrigues(phi / np.linalg.norm(phi) * rng.uniform(0.3, 1.4))[0]
        T[:3, 3] = rng.uniform(-500, 500, size=3)
        T_wm.append(T)
        T_ct.append(np.linalg.inv(T @ T_he) @ T_target)
    T_wm, T_ct = np.array(T_wm), np.array(T_ct)

    d_t, d_r = residuals_about_mean(implied_world_target(T_wm, T_he, T_ct))
    assert d_t.max() < 1e-6, f"residual should vanish, got {d_t.max()} mm"
    # Rotation tolerance is looser than translation because arccos is
    # ill-conditioned near identity: a rotation matrix accurate to 1e-12
    # still reads as ~1e-6 deg through arccos((tr-1)/2). Anything below
    # 1e-4 deg here is floating point, not a real residual.
    assert d_r.max() < 1e-4, f"residual should vanish, got {d_r.max()} deg"

    sol = solve_all_methods(T_wm, T_ct)["PARK"]
    assert np.linalg.norm(sol[:3, 3] - T_he[:3, 3]) < 1e-6
    assert rotation_diff_deg(sol[:3, :3], T_he[:3, :3]) < 1e-4

    print("self-test PASSED: helpers, residual and solve path all check out.")


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true",
                    help="run the synthetic checks and exit")
    ap.add_argument("--root", default="data/calib")
    ap.add_argument("--runs", nargs="+", default=None,
                    help="one or more calibration runs; two or more enables "
                         "the cross-session comparison")
    ap.add_argument("--method", default="PARK", choices=list(HAND_EYE_METHODS),
                    help="method whose solution is carried into the residual, "
                         "reprojection and cross-session sections")

    ap.add_argument("--squares-x", type=int, default=12)
    ap.add_argument("--squares-y", type=int, default=9)
    ap.add_argument("--square-mm", type=float, default=15.0,
                    help="measured, not the PDF design value")
    ap.add_argument("--marker-mm", type=float, default=11.25)
    ap.add_argument("--dict", default="DICT_5X5_1000")
    ap.add_argument("--min-corners", type=int, default=12)
    ap.add_argument("--max-reproj-error", type=float, default=1.0)

    ap.add_argument("--stationary-deg-s", type=float, default=5.0,
                    help="marker angular speed below which a frame counts as still")
    ap.add_argument("--min-stationary", type=int, default=30,
                    help="fewest still frames worth re-solving from")
    ap.add_argument("--velocity-bins", type=int, default=4)

    ap.add_argument("--time-offset-sweep", action="store_true",
                    help="search for a camera-minus-tracker timing offset")
    ap.add_argument("--tau-max-ms", type=float, default=40.0)
    ap.add_argument("--tau-step-ms", type=float, default=10.0)

    ap.add_argument("--no-cache", action="store_true",
                    help="redetect the board instead of using board_poses.npz")
    ap.add_argument("--out", default=None, help="write the full report as JSON")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.runs:
        ap.error("--runs is required unless --self-test")

    results = [analyse_run(run, args) for run in args.runs]
    report = {"method": args.method, "runs": results,
              "cross_session": compare_sessions(results, args)}

    if args.out:
        json.dump(report, open(args.out, "w"), indent=2, default=float)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
