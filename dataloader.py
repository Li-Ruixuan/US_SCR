"""
Dataloader for relative pose regression (RPR). Basic version.

A sample is a window of T *consecutive* frames (spaced frame_gap rows apart).
Target per step, in the camera frame:

    T_world_cam = T_world_marker @ T_marker_cam
    T_k_k1      = invert_se3(T_world_cam[k]) @ T_world_cam[k+1]
    xi          = se3_log(T_k_k1)            # [rho mm | phi rad]

Runs are split into segments at occluded frames, bad-depth frames, missing
US (sweeps) and time jumps. Windows never cross a segment; a segment is one
trajectory. The frame set does not depend on use_depth / use_us, so the
ablation arms see identical windows.

Room scans: US input is zeros with us_valid=False (model should skip the branch).
No zoom augmentation: the network never sees K, so zoom changes apparent motion.
"""

from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import cv2
import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset

from geometry import (POSE_UNITS, compose, invert_se3, load_intrinsics,
                      load_marker_poses, se3_log)

IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


@dataclass
class RPRConfig:
    T_marker_cam: np.ndarray = field(default_factory=lambda: np.eye(4))  # mm
    pose_units: str = "mm"

    seq_len: int = 2           # T frames per window
    frame_gap: int = 1         # rows between window frames
    window_step: int = 1       # rows between window starts
    max_step_s: float = 0.15   # time jump that breaks a segment (> 0.1: 2 dropped frames = 100 ms)
    spike_factor: float = 5.0  # step > factor * run p99 breaks a segment (as inspect_data.py)

    use_depth: bool = False
    use_us: bool = False
    rgb_from_us: bool = False  # US-only arm: the US crop replaces the RGB frame as the image input
    use_rgb: bool = True       # False: US-only model with its own US branch; RGB is not loaded
    us_gain: float = 0.25      # train only: US gain x(1 +- us_gain) and gamma, per window

    image_size: Tuple[int, int] = (360, 640)   # (H, W)
    us_size: Tuple[int, int] = (240, 320)      # (H, W): half the 640x480 calibration grid, keeps 4:3
    min_depth: float = 100.0                   # mm
    max_depth: float = 3000.0                  # mm

    augment: bool = False
    reverse_prob: float = 0.0  # train only: play the window backwards
    brightness: float = 0.15
    contrast: float = 0.15

    target_mean: np.ndarray = field(default_factory=lambda: np.zeros(6))
    target_std: np.ndarray = field(default_factory=lambda: np.ones(6))

    @property
    def span(self) -> int:
        return (self.seq_len - 1) * self.frame_gap


def chain_config(cfg: RPRConfig) -> RPRConfig:
    """Windows tile each segment end to end (for trajectory evaluation)."""
    return dataclasses.replace(cfg, window_step=cfg.span, augment=False)


def load_hand_eye(path, units: str) -> np.ndarray:
    T = np.load(path).astype(np.float64)
    T[:3, 3] *= POSE_UNITS[units]
    return T


def load_us_roi(run_dir: Path) -> Tuple[int, int, int, int]:
    """us_roi.json: {"version": 1, "start": [x0, y0], "end": [x1, y1]}"""
    roi = json.load(open(run_dir / "us_roi.json"))
    (x0, y0), (x1, y1) = roi["start"], roi["end"]
    if not (0 <= x0 < x1 and 0 <= y0 < y1):
        raise ValueError(f"{run_dir / 'us_roi.json'}: need 0 <= start < end, "
                         f"got start={roi['start']} end={roi['end']}")
    return int(x0), int(y0), int(x1), int(y1)


def split_segments(ok, stamps, T_world_cam, max_step_s, spike_factor):
    """Unusable rows are skipped like dropped frames; segments break only where
    the time between consecutive usable rows exceeds max_step_s, or at a spike
    (step > spike_factor * the run's p99 step). Shared with inspect_data.py."""
    idx = np.flatnonzero(ok)
    jump = np.diff(stamps[idx]) > max_step_s
    step = np.linalg.norm(np.diff(T_world_cam[idx, :3, 3], axis=0), axis=1)
    thr = spike_factor * np.percentile(step[~jump], 99)
    spike = ~jump & (step > thr)
    segments = [s for s in np.split(idx, np.flatnonzero(jump | spike) + 1) if len(s) >= 2]
    return segments, {"jumps": int(jump.sum()), "spikes": int(spike.sum()), "thr": float(thr)}


class RPRDataset(Dataset):
    def __init__(self, root, runs: Sequence[str], scan_runs: Sequence[str],
                 cfg: RPRConfig):
        self.root, self.cfg = Path(root), cfg
        self.runs = {}
        self.index: List[Tuple[str, int, np.ndarray]] = []   # (run, segment, frames)
        for name in runs:
            run = self._load_run(name, is_scan=name in set(scan_runs))
            self.runs[name] = run
            for sid, seg in enumerate(run["segments"]):
                for p in range(0, len(seg) - cfg.span, cfg.window_step):
                    self.index.append((name, sid, seg[p:p + cfg.span + 1:cfg.frame_gap]))

    def _load_run(self, name: str, is_scan: bool) -> dict:
        cfg, d = self.cfg, self.root / name
        rec_units = json.load(open(d / "record_config.json"))["pose"]["units"]
        if rec_units != cfg.pose_units:
            raise ValueError(f"{name}: record_config.json says pose units "
                             f"'{rec_units}', config has '{cfg.pose_units}'")
        T_world_marker, valid, df = load_marker_poses(d / "frames.csv", cfg.pose_units)
        K, depth_scale = load_intrinsics(d / "camera_info.json")
        info = json.load(open(d / "camera_info.json"))
        hw = (int(info["height"]), int(info["width"]))
        stamps = df["timestamp"].to_numpy(np.float64)

        ok = valid.copy()
        for i in np.flatnonzero(ok):
            with Image.open(d / df["depth"].iloc[i]) as im:
                if (im.height, im.width) != hw:        # dropped align_depth
                    ok[i] = False
            if not is_scan and not isinstance(df["us"].iloc[i], str):
                ok[i] = False
        n_air = 0
        if not is_scan and "us_air" in df.columns:     # probe off the skin (placing / lifting it)
            air = (pd.to_numeric(df["us_air"], errors="coerce") == 1).to_numpy()
            n_air = int((ok & air).sum())
            ok &= ~air

        T_world_cam = compose(T_world_marker, cfg.T_marker_cam)
        segments, info = split_segments(ok, stamps, T_world_cam,
                                        cfg.max_step_s, cfg.spike_factor)
        print(f"  {name}: {len(df)} rows, {sum(map(len, segments))} usable "
              f"({len(df) - int(ok.sum())} skipped{f', {n_air} with the probe in air' if n_air else ''}), {len(segments)} segments "
              f"({info['jumps']} time jumps, {info['spikes']} spikes > {info['thr']:.2f} mm)")
        return {"df": df, "stamps": stamps, "K": K, "depth_scale": depth_scale,
                "hw": hw, "is_scan": is_scan, "segments": segments,
                "T_world_cam": T_world_cam,
                "us_roi": load_us_roi(d) if (cfg.use_us or cfg.rgb_from_us) and not is_scan else None}

    # -- targets -----------------------------------------------------------
    @staticmethod
    def relative_targets(T_world_cam: np.ndarray) -> np.ndarray:
        """(T, 4, 4) -> (T-1, 6)"""
        return se3_log(invert_se3(T_world_cam[:-1]) @ T_world_cam[1:])

    # -- images ------------------------------------------------------------
    def _resize(self, img, interp):
        """RGB and depth are never cropped: the full field of view is resized."""
        H, W = self.cfg.image_size
        return cv2.resize(img, (W, H), interpolation=interp)

    def __len__(self):
        return len(self.index)

    def load_frame(self, name: str, i: int, bc=None):
        """One row -> (rgb (3,H,W), depth (1,H,W) | None, mask | None, us (1,h,w) | None).
        bc = (brightness, contrast) augmentation, the same for every frame of a sample;
        an optional third element is a per-channel RGB gain (3,) (anchor pairs only)."""
        cfg = self.cfg
        run, d = self.runs[name], self.root / name
        df = run["df"]
        if cfg.rgb_from_us:                    # US-only arm: the US crop takes the RGB slot
            if run["is_scan"]:
                raise ValueError(f"{name}: rgb_from_us needs US images; room scans have none")
            x0, y0, x1, y1 = run["us_roi"]
            g = cv2.imread(str(d / df["us"].iloc[i]), cv2.IMREAD_GRAYSCALE)[y0:y1, x0:x1]
            rgb = np.repeat(self._resize(g.astype(np.float32) / 255, cv2.INTER_AREA)[..., None], 3, 2)
        elif not cfg.use_rgb:                  # US-only model: no RGB input needed
            return np.zeros((3, 1, 1), np.float32), None, None, self._load_us(run, d, df, i)
        else:
            rgb = cv2.cvtColor(cv2.imread(str(d / df["rgb"].iloc[i])), cv2.COLOR_BGR2RGB)
            rgb = self._resize(rgb.astype(np.float32) / 255, cv2.INTER_AREA)
        if bc is not None:
            if len(bc) > 2:
                rgb = rgb * np.asarray(bc[2], np.float32)
            rgb = np.clip((rgb - 0.5) * bc[1] + 0.5 + bc[0], 0, 1)
        rgb = ((rgb - IMAGENET_MEAN) / IMAGENET_STD).transpose(2, 0, 1)

        dep = msk = us = None
        if cfg.use_depth:
            dep = cv2.imread(str(d / df["depth"].iloc[i]), cv2.IMREAD_UNCHANGED)
            dep = self._resize(dep.astype(np.float32) * run["depth_scale"], cv2.INTER_NEAREST)
            m = (dep > cfg.min_depth) & (dep < cfg.max_depth)
            dep, msk = np.where(m, cfg.min_depth / np.maximum(dep, 1), 0)[None], m[None]

        if cfg.use_us:
            us = self._load_us(run, d, df, i)
        return rgb, dep, msk, us

    def _load_us(self, run, d, df, i):
        cfg = self.cfg
        if run["is_scan"]:
            return np.zeros((1, *cfg.us_size))
        x0, y0, x1, y1 = run["us_roi"]
        us = cv2.imread(str(d / df["us"].iloc[i]), cv2.IMREAD_GRAYSCALE)
        return cv2.resize(us[y0:y1, x0:x1], cfg.us_size[::-1], interpolation=cv2.INTER_AREA)[None] / 255

    def augment_bc(self):
        """Random (brightness, contrast) if augmenting, else None."""
        cfg = self.cfg
        if not cfg.augment:
            return None
        return (np.random.uniform(-cfg.brightness, cfg.brightness),
                1 + np.random.uniform(-cfg.contrast, cfg.contrast))

    def __getitem__(self, n: int) -> dict:
        cfg = self.cfg
        name, sid, frames = self.index[n]
        if cfg.augment and np.random.rand() < cfg.reverse_prob:
            frames = frames[::-1].copy()       # targets follow: log(inv T) = -log T
        run = self.runs[name]
        bc = self.augment_bc()                 # same exposure change for every frame

        rgb_s, dep_s, msk_s, us_s = [], [], [], []
        for i in frames:
            rgb, dep, msk, us = self.load_frame(name, i, bc)
            rgb_s.append(rgb)
            if cfg.use_depth:
                dep_s.append(dep)
                msk_s.append(msk)
            if cfg.use_us:
                us_s.append(us)

        T_world_cam = run["T_world_cam"][frames]
        xi_raw = self.relative_targets(T_world_cam)
        out = {
            "rgb": torch.from_numpy(np.stack(rgb_s).astype(np.float32)),
            "xi": torch.from_numpy(((xi_raw - cfg.target_mean) / cfg.target_std)
                                   .astype(np.float32)),
            "xi_raw": torch.from_numpy(xi_raw),                 # float64, eval only
            "T_world_cam": torch.from_numpy(T_world_cam),       # float64, eval only
            "dt": torch.from_numpy(np.abs(np.diff(run["stamps"][frames])).astype(np.float32)),
            "frames": torch.from_numpy(frames),
            "run": name,
            "segment": sid,
        }
        if cfg.use_depth:
            out["depth"] = torch.from_numpy(np.stack(dep_s).astype(np.float32))
            out["depth_mask"] = torch.from_numpy(np.stack(msk_s).astype(np.float32))
        if cfg.use_us:
            us = np.stack(us_s).astype(np.float32)
            if cfg.augment and cfg.us_gain:     # same scanner-gain / gamma change for every frame
                g = 1 + np.random.uniform(-cfg.us_gain, cfg.us_gain)
                gam = np.exp(np.random.uniform(-cfg.us_gain, cfg.us_gain))
                us = np.clip(us ** gam * g, 0, 1).astype(np.float32)
            out["us"] = torch.from_numpy(us)
            out["us_valid"] = torch.tensor(not run["is_scan"])
        return out


# ---------------------------------------------------------------------------
# Folds, statistics, baseline
# ---------------------------------------------------------------------------

def discover_runs(root) -> List[str]:
    return sorted(p.name for p in Path(root).iterdir()
                  if (p / "frames.csv").exists() and (p / "camera_info.json").exists())


def leave_one_sweep_out(root, scan_runs):
    """[(train_runs, val_runs), ...]; scans always in train, one sweep held out."""
    runs = discover_runs(root)
    missing = set(scan_runs) - set(runs)
    if missing:
        raise ValueError(f"--scan-runs not found under {root}: {sorted(missing)}")
    scans =[r for r in runs if r in scan_runs]
    sweeps = [r for r in runs if r not in scan_runs]
    return [(scans + [s for s in sweeps if s != v], [v]) for v in sweeps]


def split_runs(root, scan_runs, fold=0, val_runs=None):
    """(train_runs, val_runs). Fixed split: val_runs named explicitly, everything else in
    root trains. Otherwise leave-one-sweep-out fold `fold`."""
    if not val_runs:
        return leave_one_sweep_out(root, scan_runs)[fold]
    runs = discover_runs(root)
    missing = (set(scan_runs) | set(val_runs)) - set(runs)
    if missing:
        raise ValueError(f"not found under {root}: {sorted(missing)}")
    if set(val_runs) & set(scan_runs):
        raise ValueError(f"a room scan cannot be a validation run: {sorted(set(val_runs) & set(scan_runs))}")
    return [r for r in runs if r not in val_runs], list(val_runs)


def test_sweeps(root, runs=None):
    """Sweeps to test on in another folder: the given runs, or every run-* there."""
    found = discover_runs(root)
    runs = runs or [r for r in found if not r.startswith("room-")]
    missing = set(runs) - set(found)
    if missing:
        raise ValueError(f"not found under {root}: {sorted(missing)}")
    return list(runs)


def compute_target_stats(ds: RPRDataset, robust: bool = False):
    """Centre/scale of xi over the TRAIN split (poses only, no images read).
    robust: median and 1.4826 * MAD, which the heavy tails do not inflate."""
    x = np.concatenate([RPRDataset.relative_targets(ds.runs[r]["T_world_cam"][f])
                        for r, _, f in ds.index])
    if robust:
        med = np.median(x, 0)
        return med, 1.4826 * np.median(np.abs(x - med), 0) + 1e-9
    return x.mean(0), x.std(0) + 1e-9


def zero_motion_baseline(ds: RPRDataset) -> dict:
    """Predict no motion. Per pair: |t| and angle of each GT step.
    Per trajectory (segment): stationary probe; final error, path, drift%."""
    g = ds.cfg.frame_gap
    t_err, r_err, traj = [], [], []
    for name, run in ds.runs.items():
        for sid, seg in enumerate(run["segments"]):
            T = run["T_world_cam"][seg[::g]]
            if len(T) < 2:
                continue
            T_k_k1 = invert_se3(T[:-1]) @ T[1:]
            t_err.append(np.linalg.norm(T_k_k1[:, :3, 3], axis=1))
            r_err.append(np.degrees(np.linalg.norm(se3_log(T_k_k1)[:, 3:], axis=1)))
            c = T[:, :3, 3]
            path = np.linalg.norm(np.diff(c, axis=0), axis=1).sum()
            final = np.linalg.norm(c[-1] - c[0])
            traj.append({"run": name, "segment": sid, "steps": len(T) - 1,
                         "path_mm": path, "final_err_mm": final,
                         "drift_pct": 100 * final / path if path > 0 else np.nan})
    t, r = np.concatenate(t_err), np.concatenate(r_err)
    return {"pair_trans_mm_median": np.median(t), "pair_rot_deg_median": np.median(r),
            "trajectory": traj}


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/train")
    ap.add_argument("--scan-runs", nargs="+", required=True)
    ap.add_argument("--hand-eye", default=None)
    ap.add_argument("--hand-eye-units", default="mm", choices=["mm", "m"])
    ap.add_argument("--seq-len", type=int, default=2)
    ap.add_argument("--frame-gap", type=int, default=1)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--max-step-s", type=float, default=0.15)
    ap.add_argument("--spike-factor", type=float, default=5.0)
    ap.add_argument("--robust-stats", action="store_true")
    args = ap.parse_args()

    T_mc = load_hand_eye(args.hand_eye, args.hand_eye_units) if args.hand_eye else np.eye(4)
    cfg = RPRConfig(T_marker_cam=T_mc, seq_len=args.seq_len, frame_gap=args.frame_gap,
                    max_step_s=args.max_step_s, spike_factor=args.spike_factor)
    folds = leave_one_sweep_out(args.root, args.scan_runs)
    train_runs, val_runs = folds[args.fold]
    print(f"{len(folds)} folds; fold {args.fold}: val={val_runs}")

    train_ds = RPRDataset(args.root, train_runs, args.scan_runs,
                          dataclasses.replace(cfg, augment=True))
    val_ds = RPRDataset(args.root, val_runs, args.scan_runs, chain_config(cfg))
    mean, std = compute_target_stats(train_ds, args.robust_stats)
    print("target mean", np.round(mean, 5), "\ntarget std ", np.round(std, 5))

    b = zero_motion_baseline(val_ds)
    print(f"\nZERO-MOTION BASELINE  per pair: {b['pair_trans_mm_median']:.3f} mm, "
          f"{b['pair_rot_deg_median']:.3f} deg (median)")
    for t in b["trajectory"]:
        print(f"  {t['run']} seg {t['segment']}: {t['steps']} steps, path "
              f"{t['path_mm']:.1f} mm, final {t['final_err_mm']:.1f} mm, "
              f"drift {t['drift_pct']:.1f}%")
