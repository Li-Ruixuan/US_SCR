"""
Relative pose regression network. Basic version.

    rgb (B, T, 3, H, W)  [+ depth, depth_mask (B, T, 1, H, W)]  [+ us (B, T, 1, h, w)]
        -> xi (B, T-1, 6), normalised, one per consecutive pair (k, k+1)

Structure
---------
per frame   RGB encoder, EfficientNet-B0 up to stride 8 (40 ch), shared weights
            + depth stem (optional) -> concat -> 1x1 conv, still stride 8
pair        [f_k, f_k1, f_k1 - f_k, local correlation]
            -> conv blocks down to stride 32 -> global average pool
            + US vectors of both frames (optional)
            -> MLP -> xi (6)

Why stride 8, and why the difference channel
--------------------------------------------
Measured motion is ~0.16 mm and ~0.05 deg per frame: under one pixel at the
input, a small fraction of a feature cell. Correlation over a displacement
window only resolves whole cells, so at stride 16/32 it would see nothing.
Keeping stride 8 and adding f_k1 - f_k gives the head the linearised signal
that sub-pixel motion produces (brightness constancy: dI ~ grad I . u).
Correlation is kept, with a small radius, for larger frame gaps and fast moves.
coarse_radius > 0 adds a second correlation on 4x average-pooled features (stride 32),
upsampled back to stride 8: +-coarse_radius cells = +-32*coarse_radius px at the input.
That is for anchor pairs (room-scan keyframe vs sweep frame, tens of pixels apart);
odometry leaves it off, and checkpoints without it load unchanged.

Pooling
-------
Global pooling before the head is correct here: the output is one pose per
pair. This is the opposite of the SCR head.

Modalities
----------
Each optional modality has its own branch and weights, so switching one off
removes a branch rather than changing the RGB encoder's input layer. US is
not spatially aligned with the camera image, so it is fused as a pooled
vector at the head. us_valid = False (room scans) zeroes the US vector and
tells the head, through an extra input, that US is missing.

The final layer has small weights (std 0.01) and zero bias: the untrained network
predicts xi ~ 0 in normalised units, i.e. about the training-set mean motion.
Exactly-zero weights would block every gradient into the network at the start.

T > 2: by default T-1 independent pairs with shared weights. temporal="gru" adds
context across the pairs of one window: a bidirectional GRU over the T-1 pair
features, added as a residual (output layer starts at zero, so an untrained
temporal model equals the pairwise one). Each step's prediction then sees the
motion of its neighbours in the window (latency: one window). Train with
--seq-len > 2 for it to matter.
"""

from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

__all__ = ["RPRNet"]


def conv_block(cin, cout, stride=1):
    return nn.Sequential(
        nn.Conv2d(cin, cout, 3, stride=stride, padding=1, bias=False),
        nn.GroupNorm(8, cout),
        nn.SiLU(inplace=True),
    )


def local_correlation(f1: torch.Tensor, f2: torch.Tensor, radius: int) -> torch.Tensor:
    """(B, C, h, w) x2 -> (B, (2r+1)^2, h, w): cosine similarity of f1 at each
    cell with f2 displaced by (dy, dx) in [-r, r]^2."""
    f1 = F.normalize(f1, dim=1)
    f2 = F.normalize(f2, dim=1)
    h, w = f1.shape[-2:]
    f2p = F.pad(f2, [radius] * 4)
    out = [(f1 * f2p[:, :, dy:dy + h, dx:dx + w]).sum(1, keepdim=True)
           for dy in range(2 * radius + 1) for dx in range(2 * radius + 1)]
    return torch.cat(out, 1)


class DepthStem(nn.Module):
    """(depth, mask) at full resolution -> stride-8 feature map."""

    def __init__(self, out_ch=32):
        super().__init__()
        self.net = nn.Sequential(
            conv_block(2, 16, 2), conv_block(16, 32, 2), conv_block(32, out_ch, 2))

    def forward(self, x):
        return self.net(x)


class USEncoder(nn.Module):
    """One US image -> one vector. Trained from scratch (no ImageNet prior)."""

    def __init__(self, out_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            conv_block(1, 16, 2), conv_block(16, 32, 2), conv_block(32, 64, 2),
            conv_block(64, 64, 2), conv_block(64, out_dim, 2),
            nn.AdaptiveAvgPool2d(1), nn.Flatten())

    def forward(self, x):
        return self.net(x)


class RPRNet(nn.Module):
    def __init__(self, use_depth: bool = False, use_us: bool = False,
                 pretrained: bool = True, corr_radius: int = 3,
                 feat_ch: int = 64, us_dim: int = 64, freeze_bn: bool = True,
                 use_dt: bool = False, coarse_radius: int = 0, temporal: str = "none",
                 us_mode: str = "vector", use_rgb: bool = True):
        super().__init__()
        self.use_depth, self.use_us, self.use_dt = use_depth, use_us, use_dt
        self.us_mode, self.use_rgb = us_mode, use_rgb
        if us_mode not in ("vector", "motion"):
            raise ValueError(f"us_mode must be 'vector' or 'motion', got {us_mode!r}")
        if not use_rgb and not (use_us and us_mode == "motion"):
            raise ValueError("use_rgb=False needs use_us=True with us_mode='motion' (US-only)")
        self.corr_radius, self.freeze_bn = corr_radius, freeze_bn
        self.coarse_radius = coarse_radius

        net = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1
                              if pretrained else None)
        self.rgb_encoder = nn.Sequential(*list(net.features)[:4])   # stride 8, 40 ch

        in_ch = 40
        if use_depth:
            self.depth_stem = DepthStem(32)
            in_ch += 32
        self.fuse = nn.Sequential(nn.Conv2d(in_ch, feat_ch, 1),
                                  nn.GroupNorm(8, feat_ch), nn.SiLU(inplace=True))

        n_corr = (2 * corr_radius + 1) ** 2
        if coarse_radius:
            n_corr += (2 * coarse_radius + 1) ** 2
        self.motion = nn.Sequential(
            conv_block(3 * feat_ch + n_corr, 128),
            conv_block(128, 128, 2),        # stride 16
            conv_block(128, 256, 2),        # stride 32
            conv_block(256, 256),
            nn.AdaptiveAvgPool2d(1), nn.Flatten())

        self.temporal = temporal
        if temporal == "gru":                # context across the pairs of a window
            self.temporal_rnn = nn.GRU(256, 128, batch_first=True, bidirectional=True)
            self.temporal_out = nn.Linear(256, 256)
            nn.init.zeros_(self.temporal_out.weight)
            nn.init.zeros_(self.temporal_out.bias)
        elif temporal != "none":
            raise ValueError(f"temporal must be 'none' or 'gru', got {temporal!r}")

        head_in = 256
        if use_us and us_mode == "motion":
            # US motion branch, built like the RGB one but with its own, fully trained weights:
            # per-image standardised US -> EfficientNet-B0 stages 1-4 (ImageNet start, batch norm
            # trained) -> [g_k, g_k1, g_k1 - g_k, correlation] -> conv -> 256. RGB and US pair
            # features are merged to 256 before the temporal module and the head.
            us_net = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None)
            self.us_encoder = nn.Sequential(*list(us_net.features)[:4])
            self.us_fuse = nn.Sequential(nn.Conv2d(40, feat_ch, 1), nn.GroupNorm(8, feat_ch), nn.SiLU(inplace=True))
            self.us_motion = nn.Sequential(
                conv_block(3 * feat_ch + (2 * corr_radius + 1) ** 2, 128),
                conv_block(128, 128, 2), conv_block(128, 256, 2), conv_block(256, 256),
                nn.AdaptiveAvgPool2d(1), nn.Flatten())
            self.pair_fuse = nn.Sequential(nn.Linear((256 if use_rgb else 0) + 256 + 1, 256), nn.SiLU(inplace=True))
        elif use_us:
            self.us_encoder = USEncoder(us_dim)
            head_in += 3 * us_dim + 1       # [u_k, u_k1, u_k1 - u_k] + valid flag
        if use_dt:
            head_in += 1                    # pair time gap, in 30 Hz frame periods
        self.head = nn.Sequential(nn.Linear(head_in, 256), nn.SiLU(inplace=True),
                                  nn.Linear(256, 6))
        nn.init.normal_(self.head[-1].weight, std=0.01)   # zero weights block all gradients at start
        nn.init.zeros_(self.head[-1].bias)

    def train(self, mode: bool = True):
        """Keep the pretrained encoder's BatchNorm statistics fixed: batches of
        a few windows give noisy statistics."""
        super().train(mode)
        if mode and self.freeze_bn:
            for m in self.rgb_encoder.modules():
                if isinstance(m, nn.BatchNorm2d):
                    m.eval()
        return self

    def forward(self, rgb: torch.Tensor,
                depth: Optional[torch.Tensor] = None,
                depth_mask: Optional[torch.Tensor] = None,
                us: Optional[torch.Tensor] = None,
                us_valid: Optional[torch.Tensor] = None,
                dt: Optional[torch.Tensor] = None) -> dict:
        B, T = (rgb if self.use_rgb else us).shape[:2]
        parts = []
        if self.use_rgb:
            parts.append(self._rgb_pairs(rgb, depth, depth_mask, B, T))
        if self.use_us and self.us_mode == "motion":
            if us is None or us_valid is None:
                raise ValueError("use_us=True needs us and us_valid")
            valid = us_valid.float().view(B, 1, 1).expand(B, T - 1, 1).reshape(-1, 1)
            parts += [self._us_pairs(us, B, T) * valid, valid]
            z = self.pair_fuse(torch.cat(parts, 1))
        else:
            z = parts[0]
        if self.temporal == "gru":
            zt = z.view(B, T - 1, -1)
            h, _ = self.temporal_rnn(zt)
            z = (zt + self.temporal_out(h)).flatten(0, 1)

        if self.use_us and self.us_mode == "vector":
            if us is None or us_valid is None:
                raise ValueError("use_us=True needs us and us_valid")
            u = self.us_encoder(us.flatten(0, 1)).view(B, T, -1)
            valid = us_valid.float().view(B, 1, 1)
            u = u * valid                                       # room scans: no US
            u1, u2 = u[:, :-1], u[:, 1:]
            zu = torch.cat([u1, u2, u2 - u1, valid.expand(B, T - 1, 1)], -1)
            z = torch.cat([z, zu.flatten(0, 1)], 1)

        if self.use_dt:
            if dt is None:
                raise ValueError("use_dt=True needs dt")
            z = torch.cat([z, (dt.float() * 30.0).reshape(-1, 1)], 1)

        return {"xi": self.head(z).view(B, T - 1, 6)}

    def _us_pairs(self, us, B, T):
        """US motion features per consecutive pair: (B*(T-1), 256)."""
        x = us.flatten(0, 1).float()                            # (B*T, 1, h, w), 0..1
        m = x.mean((2, 3), keepdim=True)
        s = x.std((2, 3), keepdim=True)
        x = ((x - m) / (s + 1e-3)).expand(-1, 3, -1, -1)       # per-image standardised, 3 channels
        g = self.us_fuse(self.us_encoder(x))
        g = g.view(B, T, *g.shape[1:])
        g1, g2 = g[:, :-1].flatten(0, 1), g[:, 1:].flatten(0, 1)
        corr = local_correlation(g1, g2, self.corr_radius)
        return self.us_motion(torch.cat([g1, g2, g2 - g1, corr], 1))

    def _rgb_pairs(self, rgb, depth, depth_mask, B, T):
        """RGB(-D) motion features per consecutive pair: (B*(T-1), 256)."""
        f = self.rgb_encoder(rgb.flatten(0, 1))
        if self.use_depth:
            if depth is None or depth_mask is None:
                raise ValueError("use_depth=True needs depth and depth_mask")
            f = torch.cat([f, self.depth_stem(
                torch.cat([depth, depth_mask], 2).flatten(0, 1))], 1)
        f = self.fuse(f)
        f = f.view(B, T, *f.shape[1:])                          # (B, T, C, h, w)

        # -- consecutive pairs, folded into the batch ------------------------
        f1 = f[:, :-1].flatten(0, 1)
        f2 = f[:, 1:].flatten(0, 1)
        corr = local_correlation(f1, f2, self.corr_radius)
        if self.coarse_radius:
            cc = local_correlation(F.avg_pool2d(f1, 4, ceil_mode=True),
                                   F.avg_pool2d(f2, 4, ceil_mode=True), self.coarse_radius)
            corr = torch.cat([corr, F.interpolate(cc, size=f1.shape[-2:], mode="nearest")], 1)
        return self.motion(torch.cat([f1, f2, f2 - f1, corr], 1))  # (B*(T-1), 256)

