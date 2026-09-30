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

Rotation is smoothed with a causal weighted geodesic (Frechet) mean on SO(3)
-- the N-rotation generalisation of SLERP note.md asks for -- rather than by
filtering quaternion/axis-angle components independently. Filtering
axis-angle components independently is *not* manifold-correct the way
per-axis translation filtering is: nearby rotations with different axes can
have a per-component median/mean that does not correspond to any sensible
intermediate rotation, which is what previously made the rotation tail
*worse* after smoothing instead of better.

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


def _rotation_frechet_mean(rots: Rotation, weights: np.ndarray, n_iter: int = 10) -> Rotation:
    """Weighted geodesic mean of a (usually small, nearby) set of rotations.

    Iteratively linearises around the running estimate -- log/exp are always
    taken in the chart centred at *that* estimate, not at identity or any
    other fixed chart, which is what keeps this correct regardless of the
    trajectory's absolute orientation. For two rotations this reduces to
    SLERP; for more it is the standard way to average points on SO(3).
    """
    mean = rots[0:1]
    for _ in range(n_iter):
        rel = mean.inv() * rots
        delta = np.average(rel.as_rotvec(), axis=0, weights=weights)
        mean = mean * Rotation.from_rotvec(delta)
        if np.linalg.norm(delta) < 1e-10:
            break
    return mean


def _causal_rotation_filter(rotations: Rotation, weights: np.ndarray,
                            median_window: int, smooth_window: int) -> Rotation:
    """Two-stage causal SO(3) filter, the rotation analogue of
    ``_causal_filter``: a robust geodesic mean over a short window (rejects a
    bad solve's rotation outright, via one reweight pass that down-weights
    whatever sits far from the window's own mean), followed by a light
    geodesic mean over the result.
    """
    n = len(weights)
    stage1 = []
    for i in range(n):
        lo = max(0, i - median_window + 1)
        window = rotations[lo:i + 1]
        w = weights[lo:i + 1]
        mean = _rotation_frechet_mean(window, w)
        resid = (mean.inv() * window).magnitude()
        scale = np.median(resid) + 1e-6
        w_robust = w / (1.0 + (resid / scale) ** 2)
        stage1.append(_rotation_frechet_mean(window, w_robust))
    stage1 = Rotation.concatenate(stage1)

    out = []
    for i in range(n):
        lo = max(0, i - smooth_window + 1)
        out.append(_rotation_frechet_mean(stage1[lo:i + 1], weights[lo:i + 1]))
    return Rotation.concatenate(out)


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

    smoothed_R = _causal_rotation_filter(
        Rotation.from_matrix(rotations), w, median_window, smooth_window).as_matrix()

    return smoothed_t, smoothed_R
