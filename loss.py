"""
Loss and the reported coordinate-error metric for scene coordinate regression.

Split out of model.py so the objective is its own unit, separate from the
network architecture. Nothing here changes the training-visible loss values;
this is a file move plus documentation/dead-code fixes (see the section D
changes referenced in each comment below), not a change to the maths.
"""

from __future__ import annotations

from typing import Tuple

import torch
import torch.nn as nn

__all__ = ["CoordinateLoss", "SequenceAuxLoss", "coordinate_metrics"]


def _coordinate_huber(xyz_norm_pred: torch.Tensor, xyz_target: torch.Tensor,
                      delta: float) -> Tuple[torch.Tensor, torch.Tensor]:
    """Per-pixel Huber on Euclidean distance, unreduced: (N, 3, h, w) ->
    (huber, dist), each (N, 1, h, w). N folds batch and any extra leading
    dims (e.g. a sequence) the caller wants to reduce over together.

    Shared by CoordinateLoss and SequenceAuxLoss so the formula is stated
    once -- two losses computing the same quantity from a copy-pasted
    formula is exactly the divergence hazard D1 removed elsewhere in this
    file; this keeps that fixed as the loss grows rather than reopening it.
    """
    diff = xyz_norm_pred.float() - xyz_target.float()
    dist = diff.pow(2).sum(dim=1, keepdim=True).clamp_min(1e-12).sqrt()
    huber = torch.where(dist < delta, 0.5 * dist.pow(2) / delta, dist - 0.5 * delta)
    return huber, dist


class CoordinateLoss(nn.Module):
    """Robust loss on scene coordinates, in normalised units.

    Huber on the Euclidean distance, not squared error per axis. Squared error
    is dominated by the worst pixels, and the worst pixels here are usually
    depth artefacts -- flying pixels at occlusion boundaries and multipath on
    glossy surfaces -- so plain L2 hands the gradient to exactly the labels you
    least believe. Huber keeps the quadratic behaviour where the network is
    already close and falls back to linear where it is not. Verified: the two
    branches agree in value and gradient at ``dist == delta``.

    There is no term to balance: everything is in millimetres. The learned
    uncertainty weighting the old PoseLoss needed existed only to reconcile
    metres with radians, and that problem does not arise under SCR.
    """

    def __init__(self, delta: float = 0.008, uncertainty: bool = False):
        super().__init__()
        # D3 (resolved, see scr_noise_reduction_plan.md item 4): at
        # scene_scale ~2000mm this normalised delta used to be a ~100mm knee
        # while calibration was pending. Calibration is no longer pending --
        # runs/scr2 (real hand-eye) settles at 17.9mm val coordinate error on
        # scene_scale=2337mm, i.e. delta ~ 18/2337 ~ 0.008 is where the knee
        # now belongs so Huber's quadratic branch stops covering essentially
        # every cell. Try 0.008 and 0.015 and compare against the 0.05 run.
        self.delta = delta              # in normalised units (~5% of scene radius)
        self.uncertainty = uncertainty

    def forward(self, pred: dict, batch: dict) -> Tuple[torch.Tensor, dict]:
        mask = batch["xyz_mask"]                        # (B, 1, h, w)
        # Force fp32 regardless of autocast. Coordinates are normalised to
        # roughly unit magnitude, where fp16 spacing is about 6e-4 -- multiplied
        # by a scene radius of ~1.5 m that is close to a millimetre, i.e. the
        # entire error budget, lost to rounding in the loss itself. The encoder
        # can run in half precision; this reduction cannot.
        huber, dist = _coordinate_huber(pred["xyz_norm"], batch["xyz"], self.delta)

        n = mask.sum().clamp_min(1.0)
        if self.uncertainty and pred["log_var"] is not None:
            # D2: this minimises at lv = ln(2 * huber) (verified numerically),
            # so the predicted quantity is the log of twice the Huber
            # residual, not a log-variance -- since Huber is linear in the
            # tail this is closer to a Laplace scale parameter. It remains
            # monotone in error, so it is still usable as a RANSAC confidence
            # weight, but it must not be reported as a learned variance.
            lv = pred["log_var"].clamp(-6.0, 6.0)
            per_px = huber * torch.exp(-lv) + 0.5 * lv
            loss = (per_px * mask).sum() / n
        else:
            loss = (huber * mask).sum() / n

        # D1: this used to also return a masked median of `dist`, computed
        # only to be discarded (both call sites did `loss, _ = crit(...)`),
        # while coordinate_metrics below recomputed the same quantity for the
        # metric that is actually reported. Deleted rather than wired up,
        # since coordinate_metrics is the already-correct, already-used path
        # (reduces once over the whole epoch, not per batch).
        return loss, {"loss": loss.detach()}


class SequenceAuxLoss(nn.Module):
    """Auxiliary per-frame coordinate loss over the whole causal window, not
    just the anchor frame CoordinateLoss supervises.

    Motivation: with dataset.py's seq_len > 1, context frames only affect
    the anchor's prediction through SCRNet's temporal_fusion -- they get no
    gradient of their own, even though every frame in the window already has
    a real tracker pose and hence a real label (dataset.py's xyz_seq /
    xyz_mask_seq). This restores that missing supervision.

    Inspired by Li et al. 2024 ("Long-Term Dependency for 3D Reconstruction
    of Freehand Ultrasound"), which uses ground truth available at other
    time steps in a sequence as auxiliary tasks (their "multi-transformation
    prediction"). Their loss also enforces consistency between *composed*
    relative transforms, which solves accumulated drift specific to their
    relative-pose-chaining formulation; that part does not apply here --
    every frame in this project is already supervised to the same absolute
    room frame (T_a_b convention), so there is nothing to compose and no
    drift between frames to add a consistency term for. Only the
    missing-supervision half of their idea transfers.

    Uses SCRNet's own aux_xyz_norm (the same CoordinateHead, shared weights,
    applied to each frame's pre-fusion features), not a second head.
    """

    def __init__(self, delta: float = 0.05):
        super().__init__()
        self.delta = delta

    def forward(self, pred: dict, batch: dict) -> torch.Tensor:
        aux_pred = pred.get("aux_xyz_norm")
        target = batch.get("xyz_seq")
        mask = batch.get("xyz_mask_seq")
        if aux_pred is None or target is None or mask is None:
            raise ValueError(
                "SequenceAuxLoss needs pred['aux_xyz_norm'] (SCRNet.forward) "
                "and batch['xyz_seq']/['xyz_mask_seq'] (dataset.py)")

        B, S = aux_pred.shape[:2]
        pred_flat = aux_pred.reshape(B * S, *aux_pred.shape[2:])
        target_flat = target.reshape(B * S, *target.shape[2:])
        mask_flat = mask.reshape(B * S, *mask.shape[2:])

        huber, _ = _coordinate_huber(pred_flat, target_flat, self.delta)
        n = mask_flat.sum().clamp_min(1.0)
        return (huber * mask_flat).sum() / n


@torch.no_grad()
def coordinate_metrics(pred: dict, batch: dict, scene_scale: float) -> torch.Tensor:
    """Per-pixel coordinate error in millimetres, as a flat tensor.

    Returns the raw errors rather than a summary. Aggregating per batch and
    averaging -- as the old train.py did with ``trans_mm_median`` -- gives a
    mean of medians, which is neither a mean nor a median. Collect the errors
    and reduce once, at the end of the epoch.
    """
    mask = batch["xyz_mask"] > 0
    diff = pred["xyz_norm"].float() - batch["xyz"].float()
    dist = diff.pow(2).sum(dim=1, keepdim=True).clamp_min(1e-12).sqrt()
    return dist[mask] * scene_scale
