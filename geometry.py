"""
Frames, transforms, and scene-coordinate labels for probe-mounted SCR.

Naming convention
-----------------
Every transform is named ``T_a_b`` and maps a point expressed in frame ``b``
into frame ``a``::

    p_a = T_a_b @ p_b

This reads left-to-right and composes by cancelling adjacent names::

    T_world_cam = T_world_marker @ T_marker_cam

The old code used ``T_wc = T_wm @ he`` with a docstring calling the result
"world-to-marker". That ambiguity is the single most common source of silent
sign/inversion errors in a tracking pipeline, so the convention above is
enforced by naming alone. If a variable is not named ``T_a_b``, it is not an
SE(3) transform.

Frames in this project
----------------------
world   NDI Polaris base frame. Fixed to the room for as long as the tracker
        is not moved. This is the "room frame" of the proposal.
marker  Rigid body of retroreflective spheres clamped to the probe. What the
        tracker actually reports.
cam     RealSense *colour* optical frame (x right, y down, z forward), which
        is what aligned_depth_to_color is registered to.
us      Ultrasound image plane. Not used here; calibrated separately.

Numerical policy
----------------
All pose and label maths is float64. The budget for this project is ~1 mm over
a room a few metres across, i.e. a relative precision of ~3e-4. float32 has
~1e-7 relative precision, so it would survive -- but rotation composition and
matrix inversion lose digits, and float64 costs nothing at these array sizes.
Casting to float32 happens once, at the boundary where tensors enter the
network, and nowhere else.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

__all__ = [
    "POSE_UNITS",
    "quat_to_matrix",
    "invert_se3",
    "compose",
    "se3_log",
    "se3_exp",
    "load_marker_poses",
    "load_intrinsics",
    "backproject",
    "scene_coordinates",
    "hand_eye_consistency",
]

# Tracker output units -> millimetres. The NDI Polaris reports millimetres;
# whether the ROS node converts is a property of the node, not of the tracker,
# so it is recorded per-run in record_config.json and passed in explicitly
# here. There is no default: a wrong guess is a silent factor of 1000.
POSE_UNITS = {"mm": 1.0, "m": 1000.0}


# ---------------------------------------------------------------------------
# SE(3) primitives
# ---------------------------------------------------------------------------

def quat_to_matrix(q: np.ndarray) -> np.ndarray:
    """(..., 4) quaternion in **(x, y, z, w)** order -> (..., 3, 3) rotation.

    geometry_msgs/Quaternion is (x, y, z, w). The NDI API natively reports
    (q0, qx, qy, qz) -- w first. Whoever wrote the tracker ROS node had to
    reorder, and that reorder is a coin flip until you check it. See
    ``check_quaternion_order`` below.
    """
    q = np.asarray(q, dtype=np.float64)
    n = np.linalg.norm(q, axis=-1, keepdims=True)
    if np.any(np.abs(n - 1.0) > 1e-3):
        warnings.warn(
            "quaternions deviate from unit norm by more than 1e-3; the tracker "
            "node may be emitting something other than a rotation",
            stacklevel=2,
        )
    q = q / n
    x, y, z, w = q[..., 0], q[..., 1], q[..., 2], q[..., 3]
    return np.stack([
        1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w),
        2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w),
        2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y),
    ], axis=-1).reshape(*q.shape[:-1], 3, 3)


def invert_se3(T: np.ndarray) -> np.ndarray:
    """Exact inverse of a rigid transform, (..., 4, 4).

    Uses the block structure ``[R | t] -> [R.T | -R.T t]`` rather than
    ``np.linalg.inv``. A general LU solve on a 4x4 is both slower and slightly
    less accurate, and -- more importantly -- it will happily invert a matrix
    that has stopped being a rotation, hiding the drift rather than surfacing it.
    """
    T = np.asarray(T, dtype=np.float64)
    R, t = T[..., :3, :3], T[..., :3, 3]
    Rt = np.swapaxes(R, -1, -2)
    out = np.zeros_like(T)
    out[..., :3, :3] = Rt
    out[..., :3, 3] = -np.einsum("...ij,...j->...i", Rt, t)
    out[..., 3, 3] = 1.0
    return out


def compose(*transforms: np.ndarray) -> np.ndarray:
    """Left-to-right composition: ``compose(T_a_b, T_b_c) -> T_a_c``."""
    out = transforms[0]
    for T in transforms[1:]:
        out = out @ T
    return out


def se3_log(T: np.ndarray) -> np.ndarray:
    """SE(3) -> se(3) as ``[rho (3) | phi (3)]``, (..., 4, 4) -> (..., 6)."""
    T = np.asarray(T, dtype=np.float64)
    R, t = T[..., :3, :3], T[..., :3, 3]
    trace = np.trace(R, axis1=-2, axis2=-1)
    cos_theta = np.clip((trace - 1.0) * 0.5, -1.0, 1.0)
    theta = np.arccos(cos_theta)[..., None]

    small = theta[..., 0] < 1e-8
    sin_theta = np.sin(theta)
    axis = np.stack([
        R[..., 2, 1] - R[..., 1, 2],
        R[..., 0, 2] - R[..., 2, 0],
        R[..., 1, 0] - R[..., 0, 1],
    ], axis=-1) / (2.0 * np.where(sin_theta < 1e-12, 1.0, sin_theta))
    phi = axis * theta

    K = _skew(axis)
    half = theta[..., None] * 0.5
    coeff = 1.0 - half * np.cos(half) / np.where(np.sin(half) < 1e-12, 1.0, np.sin(half))
    eye = np.broadcast_to(np.eye(3), K.shape)
    V_inv = eye - 0.5 * theta[..., None] * K + coeff * (K @ K)
    rho = np.einsum("...ij,...j->...i", V_inv, t)

    rho = np.where(small[..., None], t, rho)
    phi = np.where(small[..., None], 0.0, phi)
    return np.concatenate([rho, phi], axis=-1)


def se3_exp(xi: np.ndarray) -> np.ndarray:
    """se(3) -> SE(3). Inverse of :func:`se3_log`. (..., 6) -> (..., 4, 4)."""
    xi = np.asarray(xi, dtype=np.float64)
    rho, phi = xi[..., :3], xi[..., 3:]
    theta = np.linalg.norm(phi, axis=-1, keepdims=True)
    safe = np.where(theta < 1e-12, 1.0, theta)
    K = _skew(phi / safe)
    t = theta[..., None]
    eye = np.broadcast_to(np.eye(3), K.shape)

    R = eye + np.sin(t) * K + (1.0 - np.cos(t)) * (K @ K)
    V = eye + ((1.0 - np.cos(t)) / np.where(t < 1e-12, 1.0, t)) * K \
        + ((t - np.sin(t)) / np.where(t < 1e-12, 1.0, t)) * (K @ K)
    R = np.where((theta[..., None] < 1e-12), eye, R)
    V = np.where((theta[..., None] < 1e-12), eye, V)

    T = np.zeros((*xi.shape[:-1], 4, 4))
    T[..., :3, :3] = R
    T[..., :3, 3] = np.einsum("...ij,...j->...i", V, rho)
    T[..., 3, 3] = 1.0
    return T


def _skew(v: np.ndarray) -> np.ndarray:
    x, y, z = v[..., 0], v[..., 1], v[..., 2]
    o = np.zeros_like(x)
    return np.stack([
        np.stack([o, -z, y], axis=-1),
        np.stack([z, o, -x], axis=-1),
        np.stack([-y, x, o], axis=-1),
    ], axis=-2)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_marker_poses(
    frames_csv: str | Path,
    units: str,
) -> Tuple[np.ndarray, np.ndarray, pd.DataFrame]:
    """Read ``frames.csv`` -> (T_world_marker, valid, df).

    Returns
    -------
    T_world_marker : (N, 4, 4) float64, millimetres. Rows where the tracker had no
        sample are filled with NaN -- deliberately, so that any accidental use
        propagates loudly instead of silently.
    valid : (N,) bool. False where ``record.py`` left the pose columns blank
        because the marker was occluded within ``--pose-max-gap``.
    df : the full dataframe, unmodified, for image paths and timestamps.

    Occlusion handling is the whole reason this function exists rather than a
    one-line read_csv. ``record.py`` writes empty pose cells when the line of
    sight to the marker is broken, which pandas reads as NaN. NaN then survives
    quaternion normalisation, matrix multiplication, and every comparison
    operator without raising, so an occluded frame becomes a training example
    with a NaN label. The only safe policy is to mask them here, once.
    """
    if units not in POSE_UNITS:
        raise ValueError(f"units must be one of {list(POSE_UNITS)}, got {units!r}")
    scale = POSE_UNITS[units]

    df = pd.read_csv(frames_csv)
    cols = ["tx", "ty", "tz", "qx", "qy", "qz", "qw"]
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{frames_csv} lacks pose columns {missing}")

    arr = df[cols].to_numpy(np.float64)
    valid = np.isfinite(arr).all(axis=1)

    T = np.full((len(df), 4, 4), np.nan)
    if valid.any():
        good = arr[valid]
        T[valid] = np.eye(4)
        T[valid, :3, :3] = quat_to_matrix(good[:, 3:7])
        T[valid, :3, 3] = good[:, 0:3] * scale

    frac = valid.mean() if len(valid) else 0.0
    if frac < 0.95:
        warnings.warn(
            f"{Path(frames_csv).parent.name}: only {100 * frac:.1f}% of frames "
            "have a tracker pose. Check line of sight, and check that the "
            "probe stayed inside the Polaris measurement volume.",
            stacklevel=2,
        )
    return T, valid, df


def load_intrinsics(camera_info_json: str | Path) -> Tuple[np.ndarray, float]:
    """``camera_info.json`` -> (K (3,3) float64, depth_scale millimetres/unit)."""
    import json
    with open(camera_info_json) as f:
        info = json.load(f)
    K = np.array(info["K"], dtype=np.float64).reshape(3, 3)
    # camera_info records metres per depth unit (0.001). The pipeline works in
    # millimetres, where the uint16 depth PNG is already the right number.
    return K, float(info.get("depth_scale", 0.001)) * 1000.0


# ---------------------------------------------------------------------------
# Scene coordinates -- the SCR label
# ---------------------------------------------------------------------------

def backproject(depth_m: np.ndarray, K: np.ndarray) -> np.ndarray:
    """(H, W) metric depth + intrinsics -> (H, W, 3) points in the camera frame.

    Assumes depth is already aligned to the colour frame, which is what
    ``align_depth.enable:=true`` gives you. Without that alignment the depth
    pixel grid belongs to the IR camera and this is wrong by the stereo
    baseline -- about 50 mm on a D435, i.e. fifty times the error budget.
    """
    H, W = depth_m.shape
    v, u = np.indices((H, W), dtype=np.float64)
    z = depth_m.astype(np.float64)
    x = (u - K[0, 2]) * z / K[0, 0]
    y = (v - K[1, 2]) * z / K[1, 1]
    return np.stack([x, y, z], axis=-1)


def scene_coordinates(
    depth_m: np.ndarray,
    K: np.ndarray,
    T_world_cam: np.ndarray,
    min_depth: float = 250.0,
    max_depth: float = 3000.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """Dense per-pixel 3D coordinates in the room frame, plus a validity mask.

    This is the SCR regression target, and it is the reason having the tracker
    changes the project rather than merely the evaluation. Standard SCR has to
    bootstrap these labels from an SfM reconstruction; here they come straight
    from ``T_world_cam`` composed with measured metric depth, at full density,
    for every frame, with no reconstruction step and no scale ambiguity.

    Computed on demand rather than cached: a 480x640 float32 label map is
    3.7 MB, so a few thousand frames per run would run to tens of gigabytes on
    disk, while regenerating it is one 3x3 matmul over the pixel grid.

    Returns
    -------
    xyz_world : (H, W, 3) float64. Undefined where ``valid`` is False.
    valid : (H, W) bool. False for missing depth (RealSense writes 0), for
        depth outside the trusted range, and everywhere if the pose is NaN.
    """
    if not np.isfinite(T_world_cam).all():
        return (np.zeros((*depth_m.shape, 3)),
                np.zeros(depth_m.shape, dtype=bool))

    valid = (depth_m > min_depth) & (depth_m < max_depth)
    xyz_cam = backproject(np.where(valid, depth_m, 0.0), K)
    R, t = T_world_cam[:3, :3], T_world_cam[:3, 3]
    xyz_world = xyz_cam @ R.T + t
    return xyz_world, valid


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

def hand_eye_consistency(
    depth_a: np.ndarray, T_world_cam_a: np.ndarray,
    depth_b: np.ndarray, T_world_cam_b: np.ndarray,
    K: np.ndarray, sample: int = 20000, seed: int = 0,
) -> dict:
    """How far apart do two views place the *same* static scene?

    The room does not move, so scene coordinates computed from two different
    viewpoints must describe the same surfaces. If the hand-eye transform is
    wrong, each view's point cloud is rotated about a wrong centre and the two
    clouds separate. This gives a target-free check on hand-eye quality using
    nothing but data you already recorded.

    It measures a lower bound on error, not the error itself: two clouds can
    agree while both being wrong if the views are close together. Use widely
    separated viewpoints with large rotation between them, since that is where
    a lever-arm error shows up most strongly.

    Returns nearest-neighbour distance statistics in millimetres. Interpreting
    them needs care -- this conflates hand-eye error with depth noise and with
    the fact that the two views do not sample identical surface points -- so
    treat it as a regression test ("did my calibration get better?") rather
    than as a calibrated number.
    """
    from scipy.spatial import cKDTree

    rng = np.random.default_rng(seed)
    pa, va = scene_coordinates(depth_a, K, T_world_cam_a)
    pb, vb = scene_coordinates(depth_b, K, T_world_cam_b)
    a, b = pa[va], pb[vb]
    if len(a) == 0 or len(b) == 0:
        raise ValueError("one of the frames has no valid depth")
    if len(a) > sample:
        a = a[rng.choice(len(a), sample, replace=False)]

    d = cKDTree(b).query(a)[0] 
    return {
        "median_mm": float(np.median(d)),
        "p90_mm": float(np.percentile(d, 90)),
        "n_points": int(len(a)),
    }


def check_quaternion_order(frames_csv: str | Path, units: str) -> dict:
    """Detect a w-first/w-last mix-up in the tracker node.

    If the node forgot to reorder NDI's (q0, qx, qy, qz) into ROS's
    (x, y, z, w), the stored ``qw`` column holds what should have been ``qx``.
    Two signatures give it away: the marker will appear to rotate wildly
    between consecutive samples at 60 Hz, and the column that is genuinely
    ``w`` will sit near 1.0 for a probe held in a roughly constant attitude.
    """
    T, valid, _ = load_marker_poses(frames_csv, units)
    q_cols = pd.read_csv(frames_csv)[["qx", "qy", "qz", "qw"]].to_numpy(np.float64)
    q = q_cols[valid]
    steps = se3_log(invert_se3(T[valid][:-1]) @ T[valid][1:])
    ang = np.degrees(np.linalg.norm(steps[:, 3:], axis=-1))
    return {
        "median_interframe_deg": float(np.median(ang)),
        "p99_interframe_deg": float(np.percentile(ang, 99)),
        "mean_abs_per_component": np.abs(q).mean(axis=0).round(3).tolist(),
        "hint": ("a median interframe rotation above ~2 deg at 60 Hz, or a "
                 "component other than qw dominating, suggests w-first/w-last "
                 "confusion in the tracker node"),
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    rng = np.random.default_rng(0)

    # exp/log round trip
    xi = rng.normal(scale=0.3, size=(64, 6))
    assert np.allclose(se3_log(se3_exp(xi)), xi, atol=1e-10), "exp/log mismatch"

    # identity edge case
    assert np.allclose(se3_exp(np.zeros(6)), np.eye(4))
    assert np.allclose(se3_log(np.eye(4)), np.zeros(6))

    # inverse
    T = se3_exp(rng.normal(scale=0.5, size=(16, 6)))
    assert np.allclose(invert_se3(T) @ T, np.eye(4), atol=1e-12), "inverse"

    # quaternion -> matrix agrees with exp on the rotation block
    phi = rng.normal(scale=0.4, size=3)
    th = np.linalg.norm(phi)
    axis = phi / th
    q = np.concatenate([axis * np.sin(th / 2), [np.cos(th / 2)]])
    assert np.allclose(quat_to_matrix(q), se3_exp(np.r_[0, 0, 0, phi])[:3, :3])

    # scene coordinates: a point at known depth lands where the pose says
    K = np.array([[600.0, 0, 320], [0, 600.0, 240], [0, 0, 1]])
    depth = np.full((8, 8), 1.5)
    T_wc = se3_exp(np.array([100.0, -200.0, 300.0, 0.05, 0.1, -0.02]))
    depth = np.full((8, 8), 1500.0)
    xyz, valid = scene_coordinates(depth, K, T_wc)
    assert valid.all()
    # round trip through the inverse pose returns the camera-frame points
    back = (xyz - T_wc[:3, 3]) @ T_wc[:3, :3]
    assert np.allclose(back[..., 2], 1500.0)

    # NaN pose yields an empty mask rather than NaN labels
    _, v_nan = scene_coordinates(depth, K, np.full((4, 4), np.nan))
    assert not v_nan.any(), "NaN pose must invalidate the whole frame"

    print("geometry.py: all checks passed")
