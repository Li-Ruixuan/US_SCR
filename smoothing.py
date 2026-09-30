"""
Causal trajectory smoothing over solved per-frame poses.

Item 1 of scr_noise_reduction_plan.md: temporal structure applied *after* the
solver, not inside the network. A hand-held probe is band-limited (median
interframe motion in this data is 0.44 mm / 0.17 deg at 30 fps), so anything
moving faster than that in the solved trajectory is estimator noise, not
probe motion, and is removable without touching the network.

Two-stage causal (past-only) filter per axis:
  1. A weighted median over a short window -- rejects a bad solve outright,
     where a linear filter would smear it across the whole window.
  2. A light weighted moving average over a shorter window -- the "SavGol"
     step, smoothing what the median filter leaves.

Rotation is filtered as an axis-angle (so(3) log) vector rather than as raw
matrix or quaternion components, so the result is a rotation rather than an
average of rotations that happens not to be orthogonal/unit.

Weight each frame by its RANSAC inlier count: a pose solved from 200 inliers
should dominate a neighbour solved from 8 (see solver.py, item 2 of the plan).
"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np
from scipy.spatial.transform import Rotation

__all__ = ["smooth_trajectory"]


def _weighted_median(x: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Per-column weighted median of x (n, d) with weights w (n,)."""
    out = np.empty(x.shape[1])
    order = np.argsort(x, axis=0)
    for c in range(x.shape[1]):
        idx = order[:, c]
        cum = np.cumsum(w[idx])
        k = np.searchsorted(cum, cum[-1] / 2.0)
        out[c] = x[idx[min(k, len(idx) - 1)], c]
    return out


def _causal_filter(values: np.ndarray, weights: np.ndarray,
                    median_window: int, smooth_window: int) -> np.ndarray:
    n = len(values)
    med = np.empty_like(values)
    for i in range(n):
        lo = max(0, i - median_window + 1)
        med[i] = _weighted_median(values[lo:i + 1], weights[lo:i + 1])

    out = np.empty_like(values)
    for i in range(n):
        lo = max(0, i - smooth_window + 1)
        w = weights[lo:i + 1]
        w = w / w.sum() if w.sum() > 0 else np.full(len(w), 1.0 / len(w))
        out[i] = (med[lo:i + 1] * w[:, None]).sum(axis=0)
    return out


def smooth_trajectory(
    translations: np.ndarray,              # (N, 3) mm, causal time order
    rotations: np.ndarray,                 # (N, 3, 3)
    weights: Optional[np.ndarray] = None,  # (N,) inlier counts; None -> uniform
    median_window: int = 5,
    smooth_window: int = 3,
) -> Tuple[np.ndarray, np.ndarray]:
    """Causal median + light-smooth filter over a solved SE(3) trajectory.

    Caller is responsible for time-ordering and for only including frames
    from a single, genuinely causal run -- this function has no notion of
    frame number or gaps, it just filters the sequence it is given.

    Returns (smoothed_translations (N, 3), smoothed_rotations (N, 3, 3)).
    """
    translations = np.asarray(translations, dtype=np.float64)
    rotations = np.asarray(rotations, dtype=np.float64)
    n = len(translations)
    if n == 0:
        return translations.copy(), rotations.copy()

    if weights is None:
        w = np.ones(n)
    else:
        # floor at 1: a frame that solved at all still deserves some vote.
        w = np.maximum(np.asarray(weights, dtype=np.float64), 1.0)

    smoothed_t = _causal_filter(translations, w, median_window, smooth_window)

    rotvec = Rotation.from_matrix(rotations).as_rotvec()
    smoothed_rotvec = _causal_filter(rotvec, w, median_window, smooth_window)
    smoothed_R = Rotation.from_rotvec(smoothed_rotvec).as_matrix()

    return smoothed_t, smoothed_R
