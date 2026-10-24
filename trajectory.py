"""
Compose per-pair predictions into trajectories and score them. Basic version.

Always reports two things together, from the same pass:
  pair        per-pair error (mm, deg) -- what the loss optimises
  trajectory  accumulated error along each segment -- what the project is
              judged on

A trajectory is one segment of a validation run (dataloader splits runs at
occlusion / bad frames / time jumps). Unanchored: every chain starts at the
GT pose of its first frame, then composes predicted steps only. Anchoring
against the room scan will later replace that start and add corrections.

Needs a validation dataset built with dataloader.chain_config, so windows
tile each segment end to end and every step is predicted exactly once.

Positions are camera centres in the world frame. Error at the US image will
differ (lever arm to the image plane, T_cam_us) -- later.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, Tuple

import numpy as np
import torch

from geometry import se3_exp
from loss import pair_errors

Key = Tuple[str, int]      # (run, segment)


def model_inputs(batch: dict, device) -> dict:
    """The only batch keys the network may see. Never poses or targets."""
    keys = ("rgb", "depth", "depth_mask", "us", "us_valid", "dt")
    return {k: batch[k].to(device, non_blocking=True) for k in keys if k in batch}


def gt_chains(ds) -> Dict[Key, dict]:
    """GT pose chain per segment, from poses only (no images read).

    {(run, seg): {"T_gt": (N, 4, 4), "xi_gt": (N-1, 6), "t": (N,), "frames": (N,) rows}}
    Frames are the union of the tiled windows, in order. The tail of a
    segment that does not fill a whole window is not evaluated.
    """
    cfg = ds.cfg
    if cfg.window_step != cfg.span:
        raise ValueError("trajectory evaluation needs a chain_config dataset")
    frames: Dict[Key, list] = defaultdict(list)
    for run, sid, f in ds.index:
        f = list(f)
        frames[(run, sid)].extend(f if not frames[(run, sid)] else f[1:])

    chains = {}
    for (run, sid), f in frames.items():
        T = ds.runs[run]["T_world_cam"][f]
        chains[(run, sid)] = {"T_gt": T, "xi_gt": ds.relative_targets(T),
                              "t": ds.runs[run]["stamps"][f], "frames": np.asarray(f)}
    return chains


@torch.no_grad()
def predict(net, loader, device, mean, std, crit=None):
    """Run the network over a chain loader (shuffle=False).

    Returns (preds, val_loss): preds = {(run, seg): (N-1, 6) xi in mm|rad}.
    """
    net.eval()
    preds: Dict[Key, list] = defaultdict(list)
    total, n = 0.0, 0
    for batch in loader:
        out = net(**model_inputs(batch, device))
        if crit is not None:
            loss, _ = crit(out, {"xi": batch["xi"].to(device)})
            total += loss.item()
            n += 1
        xi = out["xi"].double().cpu().numpy() * std + mean      # (B, T-1, 6)
        for b in range(xi.shape[0]):
            preds[(batch["run"][b], int(batch["segment"][b]))].append(xi[b])
    preds = {k: np.concatenate(v, 0) for k, v in preds.items()}
    return preds, (total / n if n else None)


def zero_motion_preds(chains: Dict[Key, dict]) -> Dict[Key, np.ndarray]:
    """Predict no motion: xi = 0 for every step."""
    return {k: np.zeros_like(c["xi_gt"]) for k, c in chains.items()}


def compose(T_start: np.ndarray, xi: np.ndarray) -> np.ndarray:
    """(4, 4) start pose + (N-1, 6) steps -> (N, 4, 4) trajectory."""
    T = [T_start]
    for step in se3_exp(xi):
        T.append(T[-1] @ step)
    return np.stack(T)


def evaluate(chains: Dict[Key, dict], preds: Dict[Key, np.ndarray],
             min_path_mm: float = 10.0) -> dict:
    """Per-pair and per-trajectory error, together.

    pair:    pooled over all steps
    traj:    one row per segment -- final / max position error (mm), final
             rotation error (deg), GT path length, drift% = final / path
    summary: median final error; median drift% over segments with
             path >= min_path_mm; aggregate drift% = sum(final) / sum(path),
             used for checkpoint selection (tiny segments cannot dominate)
    """
    t_all, r_all, rows = [], [], []
    for key, c in chains.items():
        xi_p = preds[key]
        if len(xi_p) != len(c["xi_gt"]):
            raise ValueError(f"{key}: {len(xi_p)} predicted steps vs "
                             f"{len(c['xi_gt'])} GT steps")
        t, r = pair_errors(torch.from_numpy(xi_p), torch.from_numpy(c["xi_gt"]),
                           np.zeros(6), np.ones(6))
        t_all.append(t)
        r_all.append(r)

        T_gt = c["T_gt"]
        T_p = compose(T_gt[0], xi_p)
        pos_err = np.linalg.norm(T_p[:, :3, 3] - T_gt[:, :3, 3], axis=1)
        R_err = T_gt[-1, :3, :3].T @ T_p[-1, :3, :3]
        rot_final = np.degrees(np.arccos(np.clip((np.trace(R_err) - 1) / 2, -1, 1)))
        path = float(np.linalg.norm(np.diff(T_gt[:, :3, 3], axis=0), axis=1).sum())
        rows.append({"run": key[0], "segment": key[1], "steps": len(xi_p),
                     "duration_s": float(c["t"][-1] - c["t"][0]),
                     "path_mm": path,
                     "final_mm": float(pos_err[-1]),
                     "max_mm": float(pos_err.max()),
                     "final_rot_deg": float(rot_final),
                     "drift_pct": 100 * float(pos_err[-1]) / path if path > 0 else float("nan")})

    t, r = np.concatenate(t_all), np.concatenate(r_all)
    long = [x["drift_pct"] for x in rows if x["path_mm"] >= min_path_mm]
    total_path = sum(x["path_mm"] for x in rows)
    return {
        "pair": {"n": int(len(t)),
                 "trans_mm_median": float(np.median(t)),
                 "trans_mm_mean": float(t.mean()),
                 "trans_mm_p95": float(np.percentile(t, 95)),
                 "rot_deg_median": float(np.median(r)),
                 "rot_deg_mean": float(r.mean())},
        "traj": rows,
        "summary": {
            "n_segments": len(rows),
            "final_mm_median": float(np.median([x["final_mm"] for x in rows])),
            "max_mm_median": float(np.median([x["max_mm"] for x in rows])),
            "drift_pct_median": float(np.median(long)) if long else float("nan"),
            "drift_pct_aggregate": 100 * sum(x["final_mm"] for x in rows) / total_path
            if total_path > 0 else float("nan"),
        },
    }


def print_report(res: dict, title: str, per_segment: bool = False) -> None:
    p, s = res["pair"], res["summary"]
    print(title)
    print(f"  pair: trans median {p['trans_mm_median']:.3f} mm (mean {p['trans_mm_mean']:.3f}, "
          f"p95 {p['trans_mm_p95']:.3f}) | rot median {p['rot_deg_median']:.3f} deg "
          f"(mean {p['rot_deg_mean']:.3f})  n={p['n']}")
    print(f"  traj: final median {s['final_mm_median']:.2f} mm, max median "
          f"{s['max_mm_median']:.2f} mm | drift median {s['drift_pct_median']:.1f}%, "
          f"aggregate {s['drift_pct_aggregate']:.1f}%  segments={s['n_segments']}")
    if per_segment:
        for x in res["traj"]:
            print(f"    {x['run']} seg {x['segment']:<3d} {x['steps']:4d} steps "
                  f"{x['duration_s']:5.1f}s path {x['path_mm']:6.1f} mm  final "
                  f"{x['final_mm']:6.2f} mm  max {x['max_mm']:6.2f} mm  "
                  f"rot {x['final_rot_deg']:5.2f} deg  drift {x['drift_pct']:5.1f}%")
