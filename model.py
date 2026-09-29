"""
Scene coordinate regression network.

Input  : RGB + inverse depth + validity mask, (B, 5, H, W)
Output : 3D coordinates in the room frame, (B, 3, H/8, W/8)

Pose is not an output. It comes from solver.py, which fits a rigid transform to
the predicted correspondences. That split is the whole point of preferring SCR
to pose regression: the network supplies correspondences, and geometry -- not a
fully connected layer -- turns them into SE(3).

No global pooling anywhere
--------------------------
The old PoseHead ended in AdaptiveAvgPool2d(1), which is correct when the
output is one vector per image and fatal when the output is one vector per
cell. Every layer here is convolutional and the spatial grid survives to the
output.

Depth enters at the first convolution
-------------------------------------
The old model encoded depth in a parallel branch and concatenated it at the
head, which is reasonable when depth only has to disambiguate a global scale.
Here the network must decide, per pixel, where a *measured* 3D point sits in
the room, so depth needs to be available while spatial detail still exists.
The stem convolution is widened from 3 to 5 input channels; the RGB weights
are copied from ImageNet and the two new channels are zero-initialised, so the
network starts numerically identical to the pretrained RGB model and learns to
use depth rather than being perturbed by it at step zero.
"""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import (EfficientNet_B0_Weights, EfficientNet_B1_Weights,
                                EfficientNet_B2_Weights, efficientnet_b0,
                                efficientnet_b1, efficientnet_b2)

__all__ = ["SCRNet", "TemporalFusion", "pixel_grid"]

_BACKBONES = {
    "efficientnet_b0": (efficientnet_b0, EfficientNet_B0_Weights.IMAGENET1K_V1, 40),
    "efficientnet_b1": (efficientnet_b1, EfficientNet_B1_Weights.IMAGENET1K_V1, 40),
    "efficientnet_b2": (efficientnet_b2, EfficientNet_B2_Weights.IMAGENET1K_V1, 48),
}


def pixel_grid(h: int, w: int, stride: int = 8, device=None) -> torch.Tensor:
    """(h*w, 2) pixel coordinates of the centres of stride-s cells.

    Must agree with the label sampling offset in dataset.py. Both use
    ``stride // 2``; if you change one, change the other, or every
    correspondence handed to PnP is displaced by half a cell.
    """
    off = stride // 2
    ys = torch.arange(h, device=device, dtype=torch.float32) * stride + off
    xs = torch.arange(w, device=device, dtype=torch.float32) * stride + off
    yy, xx = torch.meshgrid(ys, xs, indexing="ij")
    return torch.stack([xx.reshape(-1), yy.reshape(-1)], dim=-1)


class CoordinateHead(nn.Module):
    """Stride-8 features -> per-cell 3D coordinates, in normalised units.

    Dilation rather than downsampling: the head needs context -- a patch of
    blank wall is ambiguous until you can see a doorway -- but pooling it away
    would destroy the per-cell output. Dilated 3x3 convolutions widen the
    receptive field at constant resolution.

    GroupNorm rather than BatchNorm. Batches here are small, and BatchNorm
    statistics from 8 samples are noisy enough to hurt; GroupNorm does not
    depend on batch size at all, which also makes train and eval behaviour
    identical.
    """

    def __init__(self, in_channels: int, width: int = 256,
                 predict_uncertainty: bool = False):
        super().__init__()
        self.predict_uncertainty = predict_uncertainty

        def block(cin, cout, dilation):
            return nn.Sequential(
                nn.Conv2d(cin, cout, 3, padding=dilation, dilation=dilation),
                nn.GroupNorm(8, cout),
                nn.SiLU(inplace=True),
            )

        self.trunk = nn.Sequential(
            block(in_channels, width, 1),
            block(width, width, 2),
            block(width, width, 4),
            block(width, width, 8),
            nn.Conv2d(width, width, 1),
            nn.GroupNorm(8, width),
            nn.SiLU(inplace=True),
        )
        out_ch = 4 if predict_uncertainty else 3
        self.out = nn.Conv2d(width, out_ch, 1)
        # Start at the scene centroid, which is zero in normalised units.
        # Without this the first epochs are spent walking a random offset back
        # to the middle of the room.
        nn.init.zeros_(self.out.weight)
        nn.init.zeros_(self.out.bias)

    def forward(self, x: torch.Tensor):
        y = self.out(self.trunk(x))
        if self.predict_uncertainty:
            # Unconstrained fourth channel; see CoordinateLoss (loss.py) for
            # what this actually trains towards -- not a Gaussian log-variance,
            # despite the name kept here for the channel/key.
            return y[:, :3], y[:, 3:4]
        return y[:, :3], None


class TemporalFusion(nn.Module):
    """Fuse S per-frame feature maps (concat + 1x1 conv) into one.

    Initialised to average the S frames channel-for-channel (weight is
    block-diagonal 1/S, bias zero), rather than an arbitrary random mixture --
    a neutral starting point with no prior about which frame in the causal
    window should matter more. When S == 1 this reduces exactly to the
    identity, so a freshly constructed seq_len=1 network behaves identically
    to the pre-sequence, single-frame SCRNet at initialisation.
    """

    def __init__(self, feat_ch: int, seq_len: int):
        super().__init__()
        self.seq_len = seq_len
        self.proj = nn.Conv2d(feat_ch * seq_len, feat_ch, 1)
        with torch.no_grad():
            self.proj.weight.zero_()
            idx = torch.arange(feat_ch)
            for k in range(seq_len):
                self.proj.weight[idx, k * feat_ch + idx, 0, 0] = 1.0 / seq_len
            self.proj.bias.zero_()

    def forward(self, feat_seq: torch.Tensor) -> torch.Tensor:
        """(B, S, C, h, w) -> (B, C, h, w)."""
        B, S, C, h, w = feat_seq.shape
        return self.proj(feat_seq.reshape(B, S * C, h, w))


class SCRNet(nn.Module):
    """RGB-D scene coordinate regressor.

    Parameters
    ----------
    seq_len : causal window length the network expects (dataset.py's
        cfg.seq_len). 1 by default -- the original single-frame network.
        Fixed at construction, unlike a batch/image-size hyperparameter,
        because the concat+1x1-conv fusion is sized for a specific S; a
        checkpoint trained with one seq_len expects exactly that many frames
        at inference.
    scene_center, scene_scale : normalisation from dataset.compute_scene_stats.
        Stored as buffers so a checkpoint is self-contained -- a model loaded
        without its scene statistics would emit coordinates in the wrong frame
        and nothing would flag it.
    predict_uncertainty : add a per-cell 4th channel. Off by default. Despite
        the "log_var" name kept for this channel/key, it is not a Gaussian
        log-variance -- see CoordinateLoss (loss.py) for what it actually
        minimises to. It gives RANSAC a principled weight and lets the loss
        down-weight pixels the network cannot place, but it also lets the
        network reduce its loss by declaring everything uncertain, so it
        needs watching.
    """

    def __init__(
        self,
        backbone: str = "efficientnet_b0",
        pretrained: bool = True,
        use_depth: bool = True,
        head_width: int = 256,
        predict_uncertainty: bool = False,
        freeze_bn: bool = True,
        seq_len: int = 1,
        scene_center: Optional[torch.Tensor] = None,
        scene_scale: float = 1.0,
    ):
        super().__init__()
        if backbone not in _BACKBONES:
            raise ValueError(f"backbone must be one of {list(_BACKBONES)}")
        ctor, weights, feat_ch = _BACKBONES[backbone]
        net = ctor(weights=weights if pretrained else None)

        self.use_depth = use_depth
        self.freeze_bn = freeze_bn
        self.stride = 8
        self.seq_len = seq_len

        features = list(net.features)[:4]        # stride 8
        if use_depth:
            features[0] = self._widen_stem(features[0])
        self.encoder = nn.Sequential(*features)
        self.temporal_fusion = TemporalFusion(feat_ch, seq_len)
        self.head = CoordinateHead(feat_ch, head_width, predict_uncertainty)

        self.register_buffer(
            "scene_center",
            torch.zeros(3) if scene_center is None else scene_center.float())
        self.register_buffer("scene_scale", torch.tensor(float(scene_scale)))

    @staticmethod
    def _widen_stem(stem: nn.Module) -> nn.Module:
        """Replace the 3-channel stem conv with a 5-channel one.

        RGB weights are preserved exactly; the depth and mask channels start at
        zero, so the first forward pass reproduces the pretrained RGB network
        and depth is learned into rather than imposed.
        """
        conv = stem[0]
        new = nn.Conv2d(5, conv.out_channels, conv.kernel_size,
                        stride=conv.stride, padding=conv.padding, bias=False)
        with torch.no_grad():
            new.weight.zero_()
            new.weight[:, :3] = conv.weight
        stem[0] = new
        return stem

    def train(self, mode: bool = True):
        """Keep encoder BatchNorm in eval mode when batches are small."""
        super().train(mode)
        if mode and self.freeze_bn:
            for m in self.encoder.modules():
                if isinstance(m, nn.BatchNorm2d):
                    m.eval()
        return self

    def forward(self, rgb: torch.Tensor,
                inv_depth: Optional[torch.Tensor] = None,
                depth_mask: Optional[torch.Tensor] = None) -> dict:
        """rgb/inv_depth/depth_mask: (B, S, C, H, W), S == self.seq_len -- a
        causal window of frames, oldest to anchor (dataset.py's __getitem__).
        Folded into the batch dimension for the shared, weight-tied
        per-frame encoder, then unfolded and fused (temporal_fusion) before
        the head, which only ever sees one feature map per sample regardless
        of S -- the rest of the network (and solver.py downstream) is
        unaware a sequence was involved at all.
        """
        B, S = rgb.shape[:2]
        if S != self.seq_len:
            raise ValueError(f"expected sequence length {self.seq_len}, got {S}")

        if self.use_depth:
            if inv_depth is None or depth_mask is None:
                raise ValueError("use_depth=True requires inv_depth and depth_mask")
            x = torch.cat([rgb, inv_depth, depth_mask], dim=2)
        else:
            x = rgb
        x = x.reshape(B * S, *x.shape[2:])

        feat_flat = self.encoder(x)                          # (B*S, C, h, w)

        # Auxiliary: the SAME head (shared weights, not a second one)
        # applied to each frame's own pre-fusion features -- this is what
        # loss.SequenceAuxLoss supervises against dataset.py's xyz_seq/
        # xyz_mask_seq, so context frames get a gradient of their own
        # instead of only influencing the anchor through temporal_fusion.
        aux_xyz_n, aux_log_var = self.head(feat_flat)
        aux_xyz_n = aux_xyz_n.reshape(B, S, *aux_xyz_n.shape[1:])
        if aux_log_var is not None:
            aux_log_var = aux_log_var.reshape(B, S, *aux_log_var.shape[1:])

        feat = feat_flat.reshape(B, S, *feat_flat.shape[1:])
        feat = self.temporal_fusion(feat)
        xyz_n, log_var = self.head(feat)                     # main (fused) prediction

        # Denormalise to millimetres in the room frame.
        centre = self.scene_center.view(1, 3, 1, 1)
        xyz = xyz_n * self.scene_scale + centre
        aux_xyz = aux_xyz_n * self.scene_scale + centre.unsqueeze(1)
        return {"xyz_norm": xyz_n, "xyz": xyz, "log_var": log_var,
                "aux_xyz_norm": aux_xyz_n, "aux_xyz": aux_xyz,
                "aux_log_var": aux_log_var}
