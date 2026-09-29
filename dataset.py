"""
Per-frame dataset for scene coordinate regression.

What changed from the pairwise dataloader
-----------------------------------------
The training example is now a single frame, not a pair. There is no motion
gate, no correlation partner, and no se(3) target. The label is a dense map of
3D points in the room frame, produced by back-projecting measured depth and
transforming by the tracker pose::

    T_world_cam = T_world_marker @ T_marker_cam
    xyz_world   = T_world_cam * backproject(depth, K)

Labels live at the network's output stride, not at input resolution
-------------------------------------------------------------------
The head predicts one 3-vector per stride-8 cell, so the loss needs one label
per cell. Labels are sampled at cell centres with nearest-neighbour lookup and
never interpolated: averaging two 3D points that straddle a depth
discontinuity produces a point floating in free space that no surface
occupies, and the network would be penalised for not predicting it.

Geometric augmentation is now allowed -- with one exception
-----------------------------------------------------------
The old dataloader excluded geometric augmentation because it would have
invalidated a single global pose target. A per-pixel target does not have that
problem: crop and scale the image, adjust the intrinsics to match, and the
geometry stays self-consistent. Rather than transform the label map alongside
the image, this module regenerates it from the augmented depth and the adjusted
K, which makes an image/label mismatch structurally impossible.

Horizontal flips remain forbidden. A mirrored image does not correspond to any
camera pose in SE(3) -- the implied transform has determinant -1 -- so a flip
asks the network to regress coordinates for a scene that cannot exist.
"""

from __future__ import annotations

import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset

from geometry import (compose, load_intrinsics, load_marker_poses,
                      scene_coordinates)

__all__ = ["SCRConfig", "SCRDataset", "compute_scene_stats", "build_splits"]

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


@dataclass
class SCRConfig:
    # -- units -------------------------------------------------------------
    # Defaults to "mm", matching record.py's own --pose-units default and the
    # project convention (note.md sec 6): the Polaris reports millimetres and
    # the dataloader works in millimetres throughout. SCRDataset.__init__
    # cross-checks this against each run's own record_config.json and raises
    # on a mismatch, so a wrong guess here does not train silently.
    pose_units: str = "mm"

    # -- extrinsics --------------------------------------------------------
    # T_marker_cam, 4x4. Required unless calibration_pending is set.
    T_marker_cam: Optional[np.ndarray] = None
    calibration_pending: bool = False

    # -- images ------------------------------------------------------------
    image_size: Tuple[int, int] = (360, 640)   # (H, W), both divisible by 8
    label_stride: int = 8                      # must match the network head
    depth_scale: float = 1.0                   # uint16 is already millimetres
    min_depth: float = 100.0
    max_depth: float = 3000.0

    # A frame whose labels are mostly invalid teaches almost nothing and
    # distorts the batch statistics. Skip it at index-build time.
    min_valid_fraction: float = 0.15

    # -- temporal averaging ------------------------------------------------
    # Default 1, i.e. off. The car rig moved at 2-5 mm/s, so averaging 8 frames
    # cost almost no blur. A probe moves at 1-5 cm/s (note section 11), an
    # order of magnitude faster, so the same window would smear several
    # millimetres -- the entire error budget -- to buy a sqrt(8) noise
    # reduction that a robust loss gets for free.
    avg_frames: int = 1

    # -- sequence (causal, multi-frame context) -----------------------------
    # Default 1: identical to the original single-frame dataset. seq_len > 1
    # stacks this many frames -- the current (anchor) frame plus
    # (seq_len - 1) earlier frames spaced seq_stride apart -- as extra
    # temporal context. The LABEL is still the anchor frame's alone; earlier
    # frames are context, not additional supervision. Causal (past-only) by
    # construction, so a network trained this way stays deployable live --
    # a centred window using future frames could not run in real time.
    # Not supported together with avg_frames > 1 (two different temporal
    # mechanisms; combining them was not asked for and adds combinatorial
    # cases for no clear benefit yet).
    seq_len: int = 1
    seq_stride: int = 1

    # -- augmentation ------------------------------------------------------
    augment: bool = False
    # Fraction of the largest crop that fits the sensor. 1.0 is the full
    # frame; smaller values crop in and magnify. Zoom-out is not available --
    # there is no image outside the sensor -- so values above 1.0 would be
    # clamped, which silently turns augmentation into a no-op.
    scale_range: Tuple[float, float] = (0.5, 1.0)
    brightness: float = 0.15
    contrast: float = 0.15
    noise_std: float = 0.01
    # Simulates the exposure and colour drift that section 6 lists as a
    # clinical nuisance. Stronger than the pairwise version, because there is
    # no second frame that has to receive an identical perturbation.

    # -- normalisation (filled by compute_scene_stats) ---------------------
    scene_center: np.ndarray = field(default_factory=lambda: np.zeros(3))
    scene_scale: float = 1.0

    def __post_init__(self):
        if any(s % self.label_stride for s in self.image_size):
            raise ValueError(
                f"image_size {self.image_size} must be divisible by "
                f"label_stride {self.label_stride}")
        if self.seq_len < 1 or self.seq_stride < 1:
            raise ValueError("seq_len and seq_stride must both be >= 1")
        if self.seq_len > 1 and self.avg_frames > 1:
            raise ValueError(
                "seq_len > 1 and avg_frames > 1 are not supported together "
                "-- pick one temporal mechanism")
        lo, hi = self.scale_range
        if not (0.0 < lo <= hi <= 1.0):
            raise ValueError(
                "scale_range must satisfy 0 < lo <= hi <= 1; it is a fraction "
                f"of the largest crop that fits the sensor, got {self.scale_range}")
        if self.T_marker_cam is None:
            if not self.calibration_pending:
                raise ValueError(
                    "T_marker_cam is required. Pass the 4x4 marker->camera "
                    "transform, or set calibration_pending=True to run with "
                    "identity for pipeline debugging only -- results from such "
                    "a run are not valid and are marked as such in every batch."
                )
            warnings.warn(
                "CALIBRATION PENDING: T_marker_cam is identity. Labels carry a "
                "pose-dependent lever-arm error and no number from this run is "
                "reportable.", stacklevel=3)
            self.T_marker_cam = np.eye(4)
        self.T_marker_cam = np.asarray(self.T_marker_cam, dtype=np.float64)
        if self.T_marker_cam.shape != (4, 4):
            raise ValueError("T_marker_cam must be 4x4")


class SCRDataset(Dataset):
    """One RGB-D frame with its dense scene-coordinate label.

    Yields
    ------
    rgb          (S, 3, H, W) float32, ImageNet-normalised, S = cfg.seq_len
    inv_depth    (S, 1, H, W) float32, normalised inverse depth
    depth_mask   (S, 1, H, W) float32, 1 where depth is usable
    xyz          (3, h, w)   float32, scene coordinates at label stride,
                             centred and scaled by the scene statistics --
                             for the ANCHOR (last, current) frame only
    xyz_mask     (1, h, w)   float32, 1 where the label is defined
    xyz_seq      (S, 3, h, w) float32, per-frame scene coordinates for every
                             frame in the window, not just the anchor --
                             auxiliary supervision (loss.SequenceAuxLoss);
                             xyz_seq[-1] duplicates xyz above
    xyz_mask_seq (S, 1, h, w) float32, per-frame version of xyz_mask
    K            (3, 3)      float32, intrinsics for the returned image
    T_world_cam  (4, 4)      float32, ground truth pose, for the solver --
                             anchor frame only
    calibrated   ()          bool, False if T_marker_cam was identity

    S is 1 by default (cfg.seq_len == 1), giving the original single-frame
    behaviour exactly -- earlier frames in the window (S > 1) are causal
    context for predicting the anchor frame's label, not extra supervision.
    """

    def __init__(self, root: str | Path, runs: Sequence[str], cfg: SCRConfig):
        self.root = Path(root)
        self.cfg = cfg
        self.runs = list(runs)

        self._df = {}
        self._T_world_cam = {}
        self._K = {}
        self._expected_hw = {}
        self.index: List[Tuple[str, int]] = []

        for run in self.runs:
            run_dir = self.root / run

            cfg_path = run_dir / "record_config.json"
            if cfg_path.exists():
                with open(cfg_path) as f:
                    rec = json.load(f)
                run_units = rec.get("pose", {}).get("units")
                if run_units is not None and run_units != cfg.pose_units:
                    raise ValueError(
                        f"{run}: record_config.json says pose units are "
                        f"{run_units!r} but the dataset was configured for "
                        f"{cfg.pose_units!r}")
            else:
                warnings.warn(
                    f"{run}: no record_config.json, so pose units cannot be "
                    f"verified; assuming {cfg.pose_units!r}", stacklevel=2)

            T_world_marker, valid, df = load_marker_poses(
                run_dir / "frames.csv", cfg.pose_units)
            K, depth_scale = load_intrinsics(run_dir / "camera_info.json")
            if abs(depth_scale - cfg.depth_scale) > 1e-9:
                warnings.warn(
                    f"{run}: camera_info depth_scale {depth_scale} differs "
                    f"from config {cfg.depth_scale}; using camera_info",
                    stacklevel=2)
            with open(run_dir / "camera_info.json") as f:
                cam_info = json.load(f)

            self._df[run] = df
            self._K[run] = K
            self._expected_hw[run] = (int(cam_info["height"]), int(cam_info["width"]))
            self._T_world_cam[run] = compose(T_world_marker, cfg.T_marker_cam)

            half = cfg.avg_frames // 2
            # Causal window ending at the anchor frame i: i - span, ...,
            # i - seq_stride, i. span=0 and window=[i] when seq_len == 1,
            # so this collapses to exactly the previous single-frame logic.
            span = (cfg.seq_len - 1) * cfg.seq_stride
            expected = self._expected_hw[run]
            n_skipped = 0
            for i in np.flatnonzero(valid):
                if not (max(half, span) <= i < len(df) - half):
                    continue
                window = range(i - span, i + 1, cfg.seq_stride)
                # Header-only read (no full decode): cheap enough to check
                # every frame in the window at dataset-construction time. A
                # handful of frames per run come back from record.py at
                # RealSense's native unaligned depth resolution instead of
                # camera_info.json's aligned size -- almost certainly a
                # one-off align_depth failure that fell back to the raw
                # stream (geometry.backproject's docstring names this
                # failure mode: wrong by the stereo baseline, ~50mm on a
                # D435, fifty times the error budget). Skip the whole window
                # outright rather than mask, since these frames were
                # recorded wrong -- one bad frame in the window invalidates
                # the sample even if the anchor frame itself is fine.
                ok = True
                for w in window:
                    if not valid[w]:
                        ok = False
                        break
                    with Image.open(run_dir / df.depth.iloc[w]) as im:
                        if (im.height, im.width) != expected:
                            ok = False
                            break
                if not ok:
                    n_skipped += 1
                    continue
                self.index.append((run, int(i)))
            if n_skipped:
                print(f"{run}: skipping {n_skipped}/{len(df)} frames "
                      "(depth-resolution mismatch, likely dropped "
                      "align_depth, somewhere in the frame or its window)")

        if not self.index:
            raise RuntimeError(
                "no frames with a tracker pose. Either the marker was occluded "
                "throughout, or the probe was outside the Polaris measurement "
                "volume for the whole run.")

    # -- IO ----------------------------------------------------------------
    def _read_rgb(self, run: str, i: int) -> np.ndarray:
        p = self.root / run / self._df[run].rgb.iloc[i]
        img = cv2.imread(str(p), cv2.IMREAD_COLOR)
        if img is None:
            raise FileNotFoundError(p)
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0

    def _read_depth(self, run: str, i: int) -> np.ndarray:
        p = self.root / run / self._df[run].depth.iloc[i]
        d = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        if d is None:
            raise FileNotFoundError(p)

        expected = self._expected_hw[run]
        if d.shape != expected:
            # The centre frame of every index entry is pre-screened for this
            # in __init__ (skipped outright, not just masked); this only
            # fires for a neighbour frame pulled in by avg_frames > 1, which
            # isn't pre-screened. Same failure mode as the one __init__
            # skips -- see the comment there -- so fall back to the same
            # "no depth" treatment rather than let a shape mismatch through.
            warnings.warn(
                f"{run} frame {i}: depth is {d.shape[1]}x{d.shape[0]}, "
                f"expected {expected[1]}x{expected[0]} -- treating as no depth.",
                stacklevel=2)
            d = np.zeros(expected, dtype=d.dtype)
        return d.astype(np.float32) * self.cfg.depth_scale

    def _load(self, run: str, i: int) -> Tuple[np.ndarray, np.ndarray]:
        """RGB and depth, optionally averaged over a short window."""
        cfg = self.cfg
        if cfg.avg_frames <= 1:
            return self._read_rgb(run, i), self._read_depth(run, i)

        half = cfg.avg_frames // 2
        lo, hi = i - half, i + half + 1
        rgb = np.mean([self._read_rgb(run, k) for k in range(lo, hi)], axis=0)

        # Mask before averaging: RealSense writes 0 for unmatched pixels, and
        # including those zeros drags valid depth toward the camera.
        acc = cnt = None
        for k in range(lo, hi):
            d = self._read_depth(run, k)
            ok = (d > cfg.min_depth) & (d < cfg.max_depth)
            acc = np.where(ok, d, 0.0) if acc is None else acc + np.where(ok, d, 0.0)
            cnt = ok.astype(np.float32) if cnt is None else cnt + ok
        keep = cnt > (hi - lo) / 2.0
        return rgb, np.where(keep, acc / np.maximum(cnt, 1.0), 0.0)

    # -- geometry-preserving augmentation ----------------------------------
    def _crop_box(self, H0: int, W0: int) -> Tuple[int, int, int, int]:
        cfg = self.cfg
        H, W = cfg.image_size
        base = min(H0 / H, W0 / W)
        if not cfg.augment:
            s = base
        else:
            lo, hi = cfg.scale_range
            s = base * np.random.uniform(lo, hi)
        ch, cw = int(round(H * s)), int(round(W * s))
        if cfg.augment:
            y0 = np.random.randint(0, H0 - ch + 1)
            x0 = np.random.randint(0, W0 - cw + 1)
        else:
            y0, x0 = (H0 - ch) // 2, (W0 - cw) // 2
        return y0, x0, ch, cw

    def _geometric(self, rgb, depth, K, box=None):
        """Crop + resize image and depth, and adjust K to match.

        K is adjusted rather than the label map being warped. The scene
        coordinates are then regenerated from the transformed depth and the
        new K, so the image and its label cannot drift out of agreement.

        box, if given, is a precomputed (y0, x0, ch, cw) rather than a freshly
        randomised one -- for a sequence sample, every frame in the window
        must share the same crop, or the frames stop being spatially aligned
        and the temporal signal is just noise. Single-frame callers (seq_len
        == 1) omit it and get the old per-call random crop, unchanged.
        """
        H, W = self.cfg.image_size
        y0, x0, ch, cw = box if box is not None else self._crop_box(*rgb.shape[:2])
        rgb = rgb[y0:y0 + ch, x0:x0 + cw]
        depth = depth[y0:y0 + ch, x0:x0 + cw]

        sx, sy = W / cw, H / ch
        rgb = cv2.resize(rgb, (W, H), interpolation=cv2.INTER_AREA)
        # Nearest for depth: bilinear would blend across occlusion boundaries
        # and manufacture surfaces that are not there.
        depth = cv2.resize(depth, (W, H), interpolation=cv2.INTER_NEAREST)

        K = K.copy()
        K[0, 2] -= x0
        K[1, 2] -= y0
        K[0, :] *= sx
        K[1, :] *= sy
        return rgb, depth, K

    def _photometric_params(self):
        """One brightness/contrast draw, shared across a whole sequence
        window -- real auto-exposure drift is slow relative to a short
        window, unlike per-pixel sensor noise, which is still drawn fresh
        per frame in _photometric below."""
        cfg = self.cfg
        b = np.random.uniform(-cfg.brightness, cfg.brightness)
        c = 1.0 + np.random.uniform(-cfg.contrast, cfg.contrast)
        return b, c

    def _photometric(self, rgb: np.ndarray, params=None) -> np.ndarray:
        cfg = self.cfg
        b, c = params if params is not None else self._photometric_params()
        rgb = np.clip((rgb - 0.5) * c + 0.5 + b, 0.0, 1.0)
        if cfg.noise_std > 0:
            rgb = np.clip(
                rgb + np.random.randn(*rgb.shape).astype(np.float32) * cfg.noise_std,
                0.0, 1.0)
        return rgb

    # -- Dataset protocol --------------------------------------------------
    def __len__(self) -> int:
        return len(self.index)

    def __getitem__(self, n: int) -> dict:
        cfg = self.cfg
        run, i = self.index[n]
        span = (cfg.seq_len - 1) * cfg.seq_stride
        window = list(range(i - span, i + 1, cfg.seq_stride))  # oldest -> anchor (i)
        K_native = self._K[run]

        # One crop box and one brightness/contrast draw shared across the
        # whole window -- every frame must get the same crop or the frames
        # stop being spatially aligned and the temporal signal is just noise.
        # Native resolution comes from _expected_hw (already validated at
        # index-build time), not a fresh load, so no frame is read twice.
        box = self._crop_box(*self._expected_hw[run])
        photo_params = self._photometric_params() if cfg.augment else None

        rgb_seq, inv_seq, mask_seq = [], [], []
        xyz_n_seq, val_l_seq = [], []
        xyz_n = val_l = K = T_world_cam = None
        s = cfg.label_stride
        off = s // 2
        for w in window:
            T_world_cam_w = self._T_world_cam[run][w]
            rgb_w, depth_w = self._load(run, w)
            rgb_w, depth_w, K_w = self._geometric(rgb_w, depth_w, K_native, box)
            if cfg.augment:
                rgb_w = self._photometric(rgb_w, photo_params)

            xyz_w, valid_w = scene_coordinates(
                depth_w, K_w, T_world_cam_w, cfg.min_depth, cfg.max_depth)

            inv_w = np.zeros_like(depth_w)
            np.divide(1.0, depth_w, out=inv_w, where=valid_w)
            inv_w = inv_w * valid_w / (1.0 / cfg.min_depth)

            rgb_n = (rgb_w - IMAGENET_MEAN) / IMAGENET_STD
            rgb_seq.append(rgb_n.transpose(2, 0, 1))
            inv_seq.append(inv_w[None].astype(np.float32))
            mask_seq.append(valid_w[None].astype(np.float32))

            # Sample labels at stride-8 cell centres for EVERY window frame,
            # not just the anchor -- xyz_seq/xyz_mask_seq below are auxiliary
            # per-frame supervision (loss.SequenceAuxLoss); every frame in
            # the window already has a real tracker pose (index-build time
            # guarantees this), so this is supervision that already existed
            # and was simply unused before. The +s//2 offset matters: a
            # stride-8 feature at index (r, c) has receptive field centred
            # on input pixel (8r + 4, 8c + 4), and using (8r, 8c) instead
            # biases every label by half a cell, which at 2m is several
            # millimetres of systematic error -- the whole budget, for free,
            # from an off-by-four.
            xyz_l_w = xyz_w[off::s, off::s]
            val_l_w = valid_w[off::s, off::s]
            xyz_n_w = (xyz_l_w - cfg.scene_center) / cfg.scene_scale
            xyz_n_w = np.where(val_l_w[..., None], xyz_n_w, 0.0)
            xyz_n_seq.append(
                np.ascontiguousarray(xyz_n_w.transpose(2, 0, 1), dtype=np.float32))
            val_l_seq.append(val_l_w[None].astype(np.float32))

            if w == i:
                xyz_n, val_l = xyz_n_w, val_l_w
                K, T_world_cam = K_w, T_world_cam_w

        return {
            "rgb": torch.from_numpy(np.ascontiguousarray(np.stack(rgb_seq))),
            "inv_depth": torch.from_numpy(np.ascontiguousarray(np.stack(inv_seq))),
            "depth_mask": torch.from_numpy(np.ascontiguousarray(np.stack(mask_seq))),
            "xyz": torch.from_numpy(
                np.ascontiguousarray(xyz_n.transpose(2, 0, 1), dtype=np.float32)),
            "xyz_mask": torch.from_numpy(val_l[None].astype(np.float32)),
            # Per-frame labels for the whole window (auxiliary supervision,
            # loss.SequenceAuxLoss); xyz_seq[-1]/xyz_mask_seq[-1] duplicate
            # xyz/xyz_mask above (same anchor frame) for a uniform shape
            # regardless of position in the window.
            "xyz_seq": torch.from_numpy(np.ascontiguousarray(np.stack(xyz_n_seq))),
            "xyz_mask_seq": torch.from_numpy(np.ascontiguousarray(np.stack(val_l_seq))),
            "K": torch.from_numpy(K.astype(np.float32)),
            "T_world_cam": torch.from_numpy(T_world_cam.astype(np.float32)),
            "calibrated": torch.tensor(not cfg.calibration_pending),
            "run": run,
            "frame": i,
        }


# ---------------------------------------------------------------------------
# Scene statistics
# ---------------------------------------------------------------------------

def compute_scene_stats(dataset: SCRDataset, n_frames: int = 200,
                        seed: int = 0) -> Tuple[np.ndarray, float]:
    """Centroid and extent of the room, from the training split only.

    SCR regresses coordinates in a frame whose origin is wherever the Polaris
    happens to sit, which can be metres from the scene. A network initialised
    near zero would spend its early epochs travelling to that offset, so the
    target is centred and scaled instead -- the same discipline as the old
    ``compute_target_stats``, applied to 3D points rather than to se(3).

    Scale is a single scalar, not per-axis. Per-axis scaling would make the
    loss anisotropic in world space: a millimetre along a short axis would cost
    more than a millimetre along a long one, and your error budget is a sphere.
    """
    rng = np.random.default_rng(seed)
    pick = rng.choice(len(dataset), min(n_frames, len(dataset)), replace=False)

    lo = np.full(3, np.inf)
    hi = np.full(3, -np.inf)
    total = np.zeros(3)
    count = 0
    for n in pick:
        run, i = dataset.index[n]
        rgb, depth = dataset._load(run, i)
        _, depth, K = dataset._geometric(rgb, depth, dataset._K[run])
        xyz, valid = scene_coordinates(
            depth, K, dataset._T_world_cam[run][i],
            dataset.cfg.min_depth, dataset.cfg.max_depth)
        p = xyz[valid]
        if not len(p):
            continue
        lo = np.minimum(lo, p.min(0))
        hi = np.maximum(hi, p.max(0))
        total += p.sum(0)
        count += len(p)

    if count == 0:
        raise RuntimeError("no valid depth in the sampled frames")
    center = total / count
    scale = float(np.max(hi - lo)) / 2.0
    return center, max(scale, 1.0)


def build_splits(root: str | Path, val_runs: Optional[Sequence[str]] = None,
                 val_fraction: float = 0.2, seed: int = 0
                 ) -> Tuple[List[str], List[str]]:
    """Split by run, with an option to name the validation runs explicitly.

    Random splitting is a convenience for early development. For anything
    reported, name the held-out runs by hand: section 9 of the note wants
    validation on held-out *trajectories*, which means the validation runs
    should follow paths the training runs did not -- different heights,
    different orientations, different parts of the room. A random split over
    runs that all trace similar paths measures interpolation, which is exactly
    the failure mode that makes APR look better than it is.
    """
    required = {"tx", "ty", "tz", "qx", "qy", "qz", "qw"}
    runs = []
    for p in sorted(Path(root).iterdir()):
        if not (p.is_dir() and (p / "frames.csv").exists()):
            continue
        header = set(pd.read_csv(p / "frames.csv", nrows=0).columns)
        if not required <= header:
            print(f"skipping {p.name}: frames.csv has no pose columns "
                  "(pre-tracker run)")
            continue
        if not (p / "camera_info.json").exists():
            print(f"skipping {p.name}: no camera_info.json")
            continue
        runs.append(p.name)

    if val_runs is not None:
        val = [r for r in val_runs if r in runs]
        missing = set(val_runs) - set(val)
        if missing:
            raise ValueError(f"validation runs not found: {sorted(missing)}")
        return [r for r in runs if r not in val], val

    rng = np.random.default_rng(seed)
    shuffled = list(runs)
    rng.shuffle(shuffled)
    n_val = max(1, int(round(len(shuffled) * val_fraction)))
    return shuffled[n_val:], shuffled[:n_val]
