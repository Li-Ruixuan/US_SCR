"""
Pose from predicted scene coordinates.

Two ways to turn correspondences into SE(3), and the choice is a real
experimental question rather than a detail.

2D-3D (PnP)
    Match each stride-8 cell's *pixel centre* against its predicted world
    point. Uses only the pixel grid on the query side, which is exact.

3D-3D (Kabsch)
    Match the *measured* camera-frame point -- back-projected from depth --
    against the predicted world point. Better conditioned in principle, and it
    uses the metric depth that motivates the RGB-D sensor.

The catch is sensor noise. RealSense stereo depth error grows with the square
of range and runs to a few centimetres at a couple of metres, whereas a pixel
coordinate is exact by construction. So 3D-3D imports noise on the query side
that 2D-3D does not have, and the theoretically better estimator may well lose.
Run both; the comparison is a figure.

Both are wrapped in RANSAC because a fraction of predicted coordinates will be
badly wrong -- most of all on frames where the sonographer's hand crosses the
lens, which section 6 names as the dominant practical failure mode. Reporting
the inlier count is what lets a frame be rejected rather than silently trusted.
"""

from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np

__all__ = ["pnp_ransac", "kabsch_ransac", "kabsch", "pose_error"]


def pnp_ransac(
    xyz_world: np.ndarray,          # (N, 3) predicted, millimetres
    uv: np.ndarray,                 # (N, 2) pixel centres
    K: np.ndarray,                  # (3, 3)
    reproj_threshold: float = 3.0,  # pixels
    iterations: int = 1000,
    confidence: float = 0.9999,
) -> Tuple[Optional[np.ndarray], np.ndarray]:
    """Returns (T_world_cam or None, inlier index array)."""
    if len(xyz_world) < 6:
        return None, np.empty(0, int)

    ok, rvec, tvec, inliers = cv2.solvePnPRansac(
        xyz_world.astype(np.float64).reshape(-1, 1, 3),
        uv.astype(np.float64).reshape(-1, 1, 2),
        K.astype(np.float64), None,
        iterationsCount=iterations,
        reprojectionError=reproj_threshold,
        confidence=confidence,
        flags=cv2.SOLVEPNP_EPNP,
    )
    if not ok or inliers is None or len(inliers) < 6:
        return None, np.empty(0, int)
    inliers = inliers.ravel()

    # Refine on the inlier set. RANSAC's estimate comes from a minimal sample;
    # the refinement is what actually buys the last fraction of a millimetre.
    rvec, tvec = cv2.solvePnPRefineLM(
        xyz_world[inliers].astype(np.float64).reshape(-1, 1, 3),
        uv[inliers].astype(np.float64).reshape(-1, 1, 2),
        K.astype(np.float64), None, rvec, tvec)

    R, _ = cv2.Rodrigues(rvec)
    # solvePnP returns the world->camera transform; we want its inverse.
    T_cam_world = np.eye(4)
    T_cam_world[:3, :3] = R
    T_cam_world[:3, 3] = tvec.ravel()
    T_world_cam = np.eye(4)
    T_world_cam[:3, :3] = R.T
    T_world_cam[:3, 3] = -R.T @ tvec.ravel()
    return T_world_cam, inliers


def kabsch(P: np.ndarray, Q: np.ndarray) -> np.ndarray:
    """Rigid transform mapping points P onto Q, both (N, 3). Returns T_q_p."""
    cp, cq = P.mean(0), Q.mean(0)
    H = (P - cp).T @ (Q - cq)
    U, _, Vt = np.linalg.svd(H)
    d = np.sign(np.linalg.det(Vt.T @ U.T))
    # The determinant correction is not optional: without it SVD will happily
    # return a reflection, which fits the points slightly better and is not a
    # rotation.
    R = Vt.T @ np.diag([1.0, 1.0, d]) @ U.T
    T = np.eye(4)
    T[:3, :3] = R
    T[:3, 3] = cq - R @ cp
    return T


def kabsch_ransac(
    xyz_world: np.ndarray,      # (N, 3) predicted world points
    xyz_cam: np.ndarray,        # (N, 3) measured camera-frame points
    threshold: float = 50.0,    # millimetres
    iterations: int = 500,
    seed: int = 0,
) -> Tuple[Optional[np.ndarray], np.ndarray]:
    """Returns (T_world_cam or None, inlier index array)."""
    n = len(xyz_world)
    if n < 3:
        return None, np.empty(0, int)
    rng = np.random.default_rng(seed)

    best_inl = np.empty(0, int)
    for _ in range(iterations):
        idx = rng.choice(n, 3, replace=False)
        T = kabsch(xyz_cam[idx], xyz_world[idx])
        pred = xyz_cam @ T[:3, :3].T + T[:3, 3]
        d = np.linalg.norm(pred - xyz_world, axis=1)
        inl = np.flatnonzero(d < threshold)
        if len(inl) > len(best_inl):
            best_inl = inl
            if len(inl) > 0.8 * n:
                break

    if len(best_inl) < 6:
        return None, np.empty(0, int)
    return kabsch(xyz_cam[best_inl], xyz_world[best_inl]), best_inl


def pose_error(T_est: np.ndarray, T_gt: np.ndarray) -> Tuple[float, float]:
    """(translation mm, rotation degrees) between two poses."""
    dt = np.linalg.norm(T_est[:3, 3] - T_gt[:3, 3])  
    R = T_est[:3, :3].T @ T_gt[:3, :3]
    cos = np.clip((np.trace(R) - 1.0) * 0.5, -1.0, 1.0)
    return float(dt), float(np.degrees(np.arccos(cos)))
