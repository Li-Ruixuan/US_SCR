#!/usr/bin/env python3
"""
Estimate T_marker_cam from a recorded ChArUco calibration session.

Data capture: an ordinary session recorded with tools/record_calibration.py,
board fixed rigidly somewhere in the room and kept in view. This tool works
offline from that run directory -- no ROS code here.

Convention mapping (verify before trusting any result -- OpenCV does not
follow this project's T_a_b convention):

    OpenCV name              This project      Source
    ------------------------  ----------------  --------------------------
    gripper2base              T_world_marker     tracker, from frames.csv
    target2cam                T_cam_target       cv2.solvePnP on the board
    cam2gripper (returned)    T_marker_cam        the answer

solvePnP returns the transform taking object points into the camera frame,
which is T_cam_target directly -- no inversion needed. The tracker gives
T_world_marker directly.

Usage:
  python3 tools/calibrate_hand_eye.py --self-test
  python3 tools/calibrate_hand_eye.py --root data --run calib_001 --out T_marker_cam.npy
  # defaults assume the calibrx-charuco-175x125mm.pdf board (DICT_6X6_250,
  # 7x5 squares) printed at the measured 24/17mm, not the 25/18mm design
  # values -- override --square-mm/--marker-mm if you re-measure and get
  # something different, e.g. after a fresh print run.

Do not run on real data until --self-test passes.
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

from geometry import invert_se3, load_intrinsics, load_marker_poses, se3_exp
from train import load_hand_eye

__all__ = ["solve_hand_eye", "check_rotational_diversity", "HAND_EYE_METHODS"]

HAND_EYE_METHODS = {
    "TSAI": cv2.CALIB_HAND_EYE_TSAI,
    "PARK": cv2.CALIB_HAND_EYE_PARK,
    "HORAUD": cv2.CALIB_HAND_EYE_HORAUD,
    "ANDREFF": cv2.CALIB_HAND_EYE_ANDREFF,
    "DANIILIDIS": cv2.CALIB_HAND_EYE_DANIILIDIS,
}


def solve_hand_eye(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam,
                   method: str) -> np.ndarray:
    """AX=XB hand-eye solve -> T_marker_cam, 4x4, translation in whatever unit
    t_gripper2base/t_target2cam were given in (mm, project-wide).

    This is the one production code path; the self-test below calls this
    same function rather than a separate implementation, so passing the
    self-test is evidence about this exact function, not a parallel one.
    """
    R, t = cv2.calibrateHandEye(R_gripper2base, t_gripper2base,
                                R_target2cam, t_target2cam,
                                method=HAND_EYE_METHODS[method])
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = t.ravel()
    return T


def check_rotational_diversity(R_world_marker: list, seed: int = 0,
                               pair_threshold_deg: float = 10.0,
                               n_pairs: int = 500) -> dict:
    """Two measures of session-wide rotational coverage, both computed over
    ALL accepted frames rather than consecutive ones.

    The translation component of a hand-eye solution is observable only
    through rotation, and only if that rotation happens about more than one
    axis: an all-parallel-axis sweep (e.g. pure yaw) leaves a whole family of
    lever arms equally consistent with the data, and the solver returns one
    of them with total confidence. This reports the spread so a degenerate
    session is visible before trusting the number it produces.

    A consecutive-frame version of this check is wrong twice over: adjacent
    accepted frames differ by ~0.2 deg of tracker jitter, occasionally
    stretched to tens of degrees by whatever gap board-detection rejection
    happened to leave between two "consecutive" accepted frames -- neither
    number is the session's actual spread, and a smooth, well-conditioned
    sweep that never drops a frame would report near-zero diversity under
    that scheme despite being exactly what this check should approve.
    """
    n = len(R_world_marker)
    if n < 2:
        return {"n": n, "orientation_spread_max_deg": 0.0,
                "max_axis_separation_deg": 0.0}

    Rs = np.stack(R_world_marker)

    # 1. Orientation spread relative to a fixed reference (first accepted
    # frame). This is what "the session swept 70 degrees" actually means;
    # consecutive differences never measure it, even when correct.
    Rel0 = np.einsum('ij,njk->nik', Rs[0].T, Rs)
    cos0 = np.clip((np.einsum('nii->n', Rel0) - 1.0) / 2.0, -1.0, 1.0)
    spread = np.degrees(np.arccos(cos0))

    # 2. Axis diversity over random PAIRS, not consecutive frames, and only
    # for pairs whose relative rotation clears pair_threshold_deg -- below
    # that the axis estimate is noise, which is exactly what corrupted the
    # old consecutive-frame version.
    rng = np.random.default_rng(seed)
    max_pairs = n * (n - 1) // 2
    target = min(n_pairs, max_pairs)
    max_attempts = max(2000, target * 50)
    seen = set()
    axes = []
    attempts = 0
    while len(axes) < target and attempts < max_attempts:
        attempts += 1
        a, b = rng.integers(0, n, 2)
        if a == b:
            continue
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        Rel = Rs[a].T @ Rs[b]
        cos = np.clip((np.trace(Rel) - 1.0) / 2.0, -1.0, 1.0)
        angle = np.degrees(np.arccos(cos))
        if angle < pair_threshold_deg:
            continue
        axis = np.array([Rel[2, 1] - Rel[1, 2],
                         Rel[0, 2] - Rel[2, 0],
                         Rel[1, 0] - Rel[0, 1]])
        norm = np.linalg.norm(axis)
        if norm < 1e-9:
            continue
        axes.append(axis / norm)

    # Axis direction only, not sign: a sweep back and forth about the same
    # physical axis must not count as two different axes. Bounded to [0, 90]
    # deg by the abs() -- not [0, 180] -- so 90 is this metric's ceiling, not
    # a sign of exceptional diversity.
    if len(axes) >= 2:
        axes = np.array(axes)
        dots = np.clip(np.abs(axes @ axes.T), -1.0, 1.0)
        max_axis_sep = float(np.degrees(np.arccos(dots)).max())
    else:
        max_axis_sep = 0.0

    return {
        "n": n,
        "orientation_spread_median_deg": float(np.median(spread)),
        "orientation_spread_p90_deg": float(np.percentile(spread, 90)),
        "orientation_spread_max_deg": float(spread.max()),
        "n_large_rotation_pairs": len(axes),
        "n_pairs_searched": attempts,
        "max_axis_separation_deg": max_axis_sep,
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test():
    """Plant a known T_marker_cam, verify solve_hand_eye recovers it exactly.

    Synthetic T_cam_target is computed directly from the planted transform,
    bypassing image formation entirely -- this tests the AX=XB solve and the
    convention mapping, not corner detection. It is deliberately not the same
    quantity a real reprojection-error check would validate.
    """
    rng = np.random.default_rng(0)

    T_marker_cam_true = se3_exp(np.array([80.0, -35.0, 45.0, 0.6, -0.4, 0.9]))
    T_world_target = se3_exp(np.array([150.0, 300.0, 2200.0, 0.1, 0.2, -0.15]))

    R_g2b, t_g2b, R_t2c, t_t2c = [], [], [], []
    for _ in range(30):
        # Wide rotational spread (~17-80 deg about a random axis) and
        # room-scale translation (mm) -- the observability condition
        # check_rotational_diversity looks for on real data.
        phi = rng.normal(size=3)
        phi = phi / np.linalg.norm(phi) * rng.uniform(0.3, 1.4)
        rho = rng.uniform(-500.0, 500.0, size=3)
        T_world_marker = se3_exp(np.concatenate([rho, phi]))

        T_cam_target = invert_se3(T_world_marker @ T_marker_cam_true) @ T_world_target

        R_g2b.append(T_world_marker[:3, :3])
        t_g2b.append(T_world_marker[:3, 3])
        R_t2c.append(T_cam_target[:3, :3])
        t_t2c.append(T_cam_target[:3, 3])

    T_est = solve_hand_eye(R_g2b, t_g2b, R_t2c, t_t2c, "TSAI")

    dt = float(np.linalg.norm(T_est[:3, 3] - T_marker_cam_true[:3, 3]))
    R_err = T_est[:3, :3].T @ T_marker_cam_true[:3, :3]
    cos = np.clip((np.trace(R_err) - 1.0) * 0.5, -1.0, 1.0)
    ang_err_deg = float(np.degrees(np.arccos(cos)))

    print(f"self-test: translation error {dt:.3e} mm, rotation error {ang_err_deg:.3e} deg")
    assert dt < 1e-6, f"self-test FAILED: translation error {dt} mm exceeds 1e-6 mm"
    assert ang_err_deg < 1e-6, f"self-test FAILED: rotation error {ang_err_deg} deg exceeds 1e-6 deg"
    print("self-test PASSED: recovered T_marker_cam matches the planted value.")
    print("It is now meaningful to run this tool on real data.")


# ---------------------------------------------------------------------------
# Real-data pipeline
# ---------------------------------------------------------------------------

def detect_board_pose(gray: np.ndarray, board, detector, K, D, min_corners: int,
                      debug: dict | None = None):
    """One frame -> (R_target2cam, t_target2cam, reproj_error_px, n_corners)
    or None if the board wasn't usable in this frame.

    If `debug` is given, it is filled in-place with whatever the detector
    found (charuco corners/ids, raw marker corners/ids) even on rejection,
    so a caller can draw it without re-running detection."""
    charuco_corners, charuco_ids, marker_corners, marker_ids = detector.detectBoard(gray)
    if debug is not None:
        debug["charuco_corners"] = charuco_corners
        debug["charuco_ids"] = charuco_ids
        debug["marker_corners"] = marker_corners
        debug["marker_ids"] = marker_ids
    if charuco_ids is None or len(charuco_ids) < min_corners:
        return None

    obj_pts, img_pts = board.matchImagePoints(charuco_corners, charuco_ids)
    if obj_pts is None or len(obj_pts) < min_corners:
        return None

    ok, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, K, D,
                                  flags=cv2.SOLVEPNP_ITERATIVE)
    if not ok:
        return None
    rvec, tvec = cv2.solvePnPRefineLM(obj_pts, img_pts, K, D, rvec, tvec)

    proj, _ = cv2.projectPoints(obj_pts, rvec, tvec, K, D)
    err = float(np.linalg.norm(
        proj.reshape(-1, 2) - img_pts.reshape(-1, 2), axis=1).mean())

    R, _ = cv2.Rodrigues(rvec)
    if debug is not None:
        debug["reproj_err"] = err
        debug["obj_pts"] = obj_pts
        debug["img_pts"] = img_pts
    return R, tvec.ravel(), err, int(len(charuco_ids))


def implied_displacement_mm(lever_mm: float, angle_deg: float) -> float:
    """Point displacement a rotation error of angle_deg implies at the tip of
    a lever_mm arm -- makes a residual interpretable against the error budget
    rather than left in the abstract (2 deg at 100mm ~ 3.5mm)."""
    return float(lever_mm * np.radians(angle_deg))


def run_real_data(args):
    run_dir = Path(args.root) / args.run
    cfg_path = run_dir / "record_config.json"
    if cfg_path.exists():
        pose_units = json.load(open(cfg_path)).get("pose", {}).get("units", "mm")
    else:
        pose_units = "mm"
        print(f"no record_config.json; assuming pose units = {pose_units!r}")

    T_world_marker_all, valid, df = load_marker_poses(run_dir / "frames.csv", pose_units)
    K, _ = load_intrinsics(run_dir / "camera_info.json")
    with open(run_dir / "camera_info.json") as f:
        D = np.array(json.load(f)["D"], dtype=np.float64)

    dictionary = aruco.getPredefinedDictionary(getattr(aruco, args.dict))
    board = aruco.CharucoBoard((args.squares_x, args.squares_y),
                               args.square_mm, args.marker_mm, dictionary)
    detector = aruco.CharucoDetector(board, aruco.CharucoParameters(),
                                     aruco.DetectorParameters())

    R_g2b, t_g2b, R_t2c, t_t2c = [], [], [], []
    n_seen, n_rejected_corners, n_rejected_reproj = 0, 0, 0
    aborted = False
    for i in np.flatnonzero(valid):
        p = run_dir / df.rgb.iloc[i]
        img_color = cv2.imread(str(p)) if args.show else None
        img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE) if img_color is None \
            else cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)
        if img is None:
            continue
        n_seen += 1
        debug = {} if args.show else None
        result = detect_board_pose(img, board, detector, K, D, args.min_corners, debug=debug)
        if result is None:
            n_rejected_corners += 1
            status, color = "REJECTED: too few corners", (0, 0, 255)
        else:
            R, t, err, n_corners = result
            if err > args.max_reproj_error:
                n_rejected_reproj += 1
                status, color = f"REJECTED: reproj err {err:.2f}px", (0, 0, 255)
            else:
                R_g2b.append(T_world_marker_all[i, :3, :3])
                t_g2b.append(T_world_marker_all[i, :3, 3])
                R_t2c.append(R)
                t_t2c.append(t)
                status, color = "ACCEPTED", (0, 255, 0)

        if args.show:
            vis = img_color.copy()
            marker_ids = debug.get("marker_ids")
            if marker_ids is not None and len(marker_ids):
                aruco.drawDetectedMarkers(vis, debug["marker_corners"], marker_ids)
            charuco_ids = debug.get("charuco_ids")
            if charuco_ids is not None and len(charuco_ids):
                aruco.drawDetectedCornersCharuco(vis, debug["charuco_corners"],
                                                 charuco_ids, (0, 0, 255))
            n_m = 0 if marker_ids is None else len(marker_ids)
            n_c = 0 if charuco_ids is None else len(charuco_ids)
            cv2.putText(vis, f"[{i}] {p.name}  markers={n_m} charuco={n_c}  {status}",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(vis, f"accepted so far: {len(R_g2b)}/{n_seen}   "
                             f"'q' quit  space to pause/step",
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)
            cv2.imshow("ChArUco detection", vis)
            key = cv2.waitKey(args.show_delay_ms) & 0xFF
            if key == ord(' '):
                key = cv2.waitKey(0) & 0xFF
            if key == ord('q'):
                print("\nstopped early by user ('q') -- solving with frames seen so far")
                aborted = True
                break

    if args.show:
        cv2.destroyAllWindows()

    print(f"{n_seen} frames with a tracker pose{' (stopped early)' if aborted else ''}; "
          f"{len(R_g2b)} usable after board detection "
          f"({n_rejected_corners} rejected: fewer than {args.min_corners} corners; "
          f"{n_rejected_reproj} rejected: reprojection error above "
          f"{args.max_reproj_error}px)")
    if len(R_g2b) < 10:
        print("WARNING: fewer than 10 usable frames. A hand-eye solve from "
              "this few poses is not trustworthy regardless of what it returns.")
        if len(R_g2b) == 0:
            return

    diversity = check_rotational_diversity(R_g2b, seed=args.seed)
    print(f"\nrotational diversity: orientation spread from first accepted "
          f"frame -- median {diversity['orientation_spread_median_deg']:.1f} deg, "
          f"p90 {diversity['orientation_spread_p90_deg']:.1f} deg, "
          f"max {diversity['orientation_spread_max_deg']:.1f} deg; "
          f"axis separation over {diversity['n_large_rotation_pairs']} pairs "
          f"above 10 deg ({diversity['n_pairs_searched']} candidates searched): "
          f"{diversity['max_axis_separation_deg']:.1f} deg")
    if diversity["orientation_spread_max_deg"] < 60.0 or diversity["max_axis_separation_deg"] < 20.0:
        print("WARNING: this session likely lacks the rotational diversity "
              "hand-eye calibration needs. The translation component is "
              "observable only through rotation about at least two "
              "non-parallel axes (ideally 60-90 deg of spread); with less "
              "than that the problem is near-degenerate and can return a "
              "confident, wrong lever arm. Treat any solution below as "
              "suspect for this reason specifically, not just in general.")

    print(f"\n{'method':12s} {'lever_mm':>10s} {'tx':>9s} {'ty':>9s} {'tz':>9s}")
    solutions = {}
    for name in HAND_EYE_METHODS:
        try:
            T = solve_hand_eye(R_g2b, t_g2b, R_t2c, t_t2c, name)
        except cv2.error as e:
            print(f"{name:12s} FAILED: {e}")
            continue
        solutions[name] = T
        lever = float(np.linalg.norm(T[:3, 3]))
        tx, ty, tz = T[:3, 3]
        print(f"{name:12s} {lever:10.1f} {tx:9.1f} {ty:9.1f} {tz:9.1f}")

    if args.method not in solutions:
        print(f"\n--method {args.method} did not produce a solution; aborting.")
        return
    T_chosen = solutions[args.method]
    print(f"\nusing --method {args.method}")

    # AX=XB residual: every frame implies the same T_world_target if the
    # hand-eye transform and every pose are exact. Disagreement between
    # frames' implied T_world_target is the direct measure of fit quality.
    T_world_target_per_frame = []
    for Rg, tg, Rt, tt in zip(R_g2b, t_g2b, R_t2c, t_t2c):
        T_wm = np.eye(4); T_wm[:3, :3] = Rg; T_wm[:3, 3] = tg
        T_ct = np.eye(4); T_ct[:3, :3] = Rt; T_ct[:3, 3] = tt
        T_world_target_per_frame.append(T_wm @ T_chosen @ T_ct)

    rng = np.random.default_rng(args.seed)
    n = len(T_world_target_per_frame)
    n_pairs = min(args.residual_pairs, n * (n - 1) // 2)
    res_t, res_r = [], []
    seen = set()
    while len(res_t) < n_pairs:
        a, b = rng.choice(n, 2, replace=False)
        key = (min(a, b), max(a, b))
        if key in seen:
            continue
        seen.add(key)
        Ta, Tb = T_world_target_per_frame[a], T_world_target_per_frame[b]
        d_t = float(np.linalg.norm(Ta[:3, 3] - Tb[:3, 3]))
        Rel = Ta[:3, :3].T @ Tb[:3, :3]
        d_r = float(np.degrees(np.arccos(np.clip((np.trace(Rel) - 1) / 2, -1, 1))))
        res_t.append(d_t)
        res_r.append(d_r)
    res_t, res_r = np.array(res_t), np.array(res_r)

    lever_mm = float(np.linalg.norm(T_chosen[:3, 3]))
    print(f"\nAX=XB residual over {len(res_t)} pairs "
          f"(disagreement in implied T_world_target):")
    print(f"  translation: median {np.median(res_t):.2f}mm  p90 {np.percentile(res_t,90):.2f}mm")
    print(f"  rotation:    median {np.median(res_r):.2f}deg p90 {np.percentile(res_r,90):.2f}deg")
    implied = implied_displacement_mm(lever_mm, float(np.median(res_r)))
    print(f"  at this solution's {lever_mm:.1f}mm lever arm, the median "
          f"rotation residual alone implies ~{implied:.2f}mm of point "
          f"displacement -- compare against the project's ~1mm budget")

    np.save(args.out, T_chosen)
    print(T_chosen)
    print(f"\nwrote {args.out} (mm) -- validating via train.load_hand_eye:")
    load_hand_eye(args.out, "mm")


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true",
                    help="run the synthetic self-test and exit; do this before ever processing real data")
    ap.add_argument("--root", default="tools")
    ap.add_argument("--run", default=None)
    ap.add_argument("--squares-x", type=int, default=7)
    ap.add_argument("--squares-y", type=int, default=5)
    ap.add_argument("--square-mm", type=float, default=24.0,
                    help="printed square size in mm -- measure the physical board, don't trust the PDF's design value; this "
                         "board's printer scaled 25mm (design) down to 24mm")
    ap.add_argument("--marker-mm", type=float, default=17.0, help="printed marker size in mm; see --square-mm")
    ap.add_argument("--dict", default="DICT_6X6_250")
    ap.add_argument("--min-corners", type=int, default=12)
    ap.add_argument("--max-reproj-error", type=float, default=1.0,
                    help="pixels; frames above this are rejected")
    ap.add_argument("--method", default="TSAI", choices=list(HAND_EYE_METHODS))
    ap.add_argument("--residual-pairs", type=int, default=100)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="T_marker_cam.npy")
    ap.add_argument("--show", action="store_true",
                    help="open a live OpenCV window showing ArUco/ChArUco "
                         "detection on each frame as it's processed")
    ap.add_argument("--show-delay-ms", type=int, default=1,
                    help="cv2.waitKey delay per frame when --show is set; "
                         "0 waits for a keypress (step through frame by frame)")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return

    if not args.run:
        ap.error("--run is required unless --self-test")
    run_real_data(args)


if __name__ == "__main__":
    main()
