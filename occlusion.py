"""
Synthetic occlusion for the robustness test: the same occluder for our system (scr_anchor.py track --occlude)
and for the RGB-D SLAM baseline (tools/slam_baseline.py export --occlude), so both see identical frames.

The occluder stands in for an arm or a hand in front of the probe camera: a textured band (skin-like colour with
a fixed noise pattern, so feature detectors find corners on it) at a near depth (default 400 mm, as a hand), over
the full image height and FRAC of the width. It appears for DUR seconds every PERIOD seconds of a sweep, starting
PERIOD / 2 s after the sweep's first row (the sweep starts unoccluded), alternating left and right side.
Room scans are never occluded.
"""

import numpy as np

_TEXTURE = {}


def occluder_window(t_rel, frac, dur, period):
    """(x0, x1) of the band as fractions of the image width at t_rel seconds into the sweep, or None."""
    if frac <= 0 or t_rel < period / 2:
        return None
    k, phase = divmod(t_rel - period / 2, period)
    if phase >= dur:
        return None
    return (0.0, frac) if int(k) % 2 == 0 else (1.0 - frac, 1.0)


def _texture(h, w):
    """(h, w, 3) float in [0, 1]: skin-like colour with a fixed blob pattern, the same at every resolution."""
    key = (h, w)
    if key not in _TEXTURE:
        import cv2
        rng = np.random.default_rng(1234)
        coarse = rng.random((18, 32, 3)).astype(np.float32)
        noise = cv2.resize(coarse, (w, h), interpolation=cv2.INTER_CUBIC)
        base = np.array([0.80, 0.60, 0.50], np.float32)
        _TEXTURE[key] = np.clip(base * (0.65 + 0.7 * noise), 0, 1)
    return _TEXTURE[key]


def occlude(rgb01, depth, t_rel, frac, dur, period, depth_value):
    """Occlude one frame in place if the occluder is up at t_rel. rgb01: (h, w, 3) float in [0, 1] or None;
    depth: (H, W) in any unit (depth_value in that unit) or None. Returns True if the frame was occluded."""
    win = occluder_window(t_rel, frac, dur, period)
    if win is None:
        return False
    if rgb01 is not None:
        h, w = rgb01.shape[:2]
        a, b = int(round(win[0] * w)), int(round(win[1] * w))
        rgb01[:, a:b] = _texture(h, w)[:, a:b]
    if depth is not None:
        h, w = depth.shape[:2]
        a, b = int(round(win[0] * w)), int(round(win[1] * w))
        depth[:, a:b] = depth_value
    return True
