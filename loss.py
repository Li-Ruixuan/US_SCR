"""
Loss and per-pair error for relative pose regression. Basic version.

Loss
----
Huber on the normalised xi (dataloader: (xi_raw - mean) / std), split into
translation (rho, 3) and rotation (phi, 3):

    loss = huber(rho) + w_rot * huber(phi)

Normalisation already puts millimetres and radians on a comparable scale
(one std each), so w_rot = 1 is a reasonable start; tune it on the
trajectory metric, not on the loss. Huber rather than L2 because the targets
are heavy-tailed (std several times the median step) and a few tracker
glitches should not own the gradient. delta is in std units.

Metric
------
pair_errors compares transforms, not 6-vectors:

    trans_mm = |t_pred - t_gt|           translation of T_k_k1, not rho
    rot_deg  = angle(R_gt^T R_pred)

so the zero-motion predictor scores exactly the GT step size, the same
number dataloader.zero_motion_baseline prints. rho differs from t once there
is rotation, so reporting error on rho would not match the baseline.
"""

from __future__ import annotations

from typing import Tuple

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

from geometry import se3_exp

__all__ = ["RPRLoss", "pair_errors"]


class RPRLoss(nn.Module):
    """kind="huber": Huber per component (robust to heavy tails).
    kind="mmae": motion-weighted L1 (MoGLo-Net, Lee et al. 2025): each pair is
    weighted by w = |xi| / max|xi| + eps over the batch, so with eps = 2 the
    fastest pair counts 1.5x the slowest. It up-weights the rarer fast moves."""

    def __init__(self, delta: float = 1.0, w_rot: float = 1.0, kind: str = "huber",
                 eps: float = 2.0):
        super().__init__()
        if kind not in ("huber", "mmae"):
            raise ValueError(f"kind must be 'huber' or 'mmae', got {kind!r}")
        self.delta, self.w_rot, self.kind, self.eps = delta, w_rot, kind, eps

    def forward(self, pred: dict, batch: dict) -> Tuple[torch.Tensor, dict]:
        xi_pred = pred["xi"].float()             # (B, T-1, 6), fp32 even under autocast
        xi_gt = batch["xi"].float()
        if self.kind == "mmae":
            mag = xi_gt.norm(dim=-1, keepdim=True)
            w = mag / mag.max().clamp_min(1e-9) + self.eps
            w = w / w.mean()                     # keep the loss on the same scale as plain L1
            err = (xi_pred - xi_gt).abs() * w
            l_t, l_r = err[..., :3].mean(), err[..., 3:].mean()
        else:
            l_t = F.huber_loss(xi_pred[..., :3], xi_gt[..., :3], delta=self.delta)
            l_r = F.huber_loss(xi_pred[..., 3:], xi_gt[..., 3:], delta=self.delta)
        loss = l_t + self.w_rot * l_r
        return loss, {"loss_t": l_t.detach(), "loss_r": l_r.detach()}


@torch.no_grad()
def pair_errors(xi_pred_norm: torch.Tensor, xi_raw_gt: torch.Tensor,
                mean: np.ndarray, std: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Per-pair (trans mm, rot deg), flattened over batch and pairs.

    xi_pred_norm: (B, T-1, 6) network output, normalised
    xi_raw_gt:    (B, T-1, 6) batch["xi_raw"], mm | rad
    """
    xi_p = xi_pred_norm.detach().double().cpu().numpy().reshape(-1, 6) * std + mean
    xi_g = xi_raw_gt.detach().double().cpu().numpy().reshape(-1, 6)
    T_p, T_g = se3_exp(xi_p), se3_exp(xi_g)
    trans = np.linalg.norm(T_p[:, :3, 3] - T_g[:, :3, 3], axis=1)
    R_err = np.swapaxes(T_g[:, :3, :3], 1, 2) @ T_p[:, :3, :3]
    cos = np.clip((np.trace(R_err, axis1=1, axis2=2) - 1.0) / 2.0, -1.0, 1.0)
    return trans, np.degrees(np.arccos(cos))
