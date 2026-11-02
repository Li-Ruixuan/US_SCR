"""
Scene coordinate regression (SCR) for anchoring: a learned anchor with geometric outlier rejection.

The network (EfficientNet-B0 encoder, as RPRNet, with a per-pixel head instead of pose
regression) predicts for every cell of a stride-8 grid the 3D room coordinate (mm, room
frame) of the surface seen there. The camera pose then follows from RANSAC on those pairs
(Kabsch with the measured depth in the final system, PnP here), so wrong predictions (moved
objects, hands, glare) are outliers, and no keyframe retrieval or prior pose is needed.

Library of the final system (scr_anchor.py, scr_map.py): the network, its training targets, depth
loading, and the PnP localisation used by baselines/anchoring.py --anchor scr. Training, tracking and
mapping are in scr_anchor.py and scr_map.py; this file's own train / eval commands were replaced by
scr_anchor.py (commit 70d9a8e has them).
"""

from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

from geometry import invert_se3

STRIDE = 8


class SCRNet(nn.Module):
    """RGB (B, 3, H, W), ImageNet-normalised -> room coordinates (B, 3, H/8, W/8) in metres,
    relative to the scene centre stored with the checkpoint."""

    def __init__(self, pretrained=True):
        super().__init__()
        f = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None).features
        self.low = f[:4]                    # stride 8, 40 channels
        self.high = f[4:6]                  # stride 16, 112 channels (wider context)
        self.head = nn.Sequential(nn.Conv2d(152, 256, 1), nn.ReLU(inplace=True),
                                  nn.Conv2d(256, 256, 1), nn.ReLU(inplace=True),
                                  nn.Conv2d(256, 256, 1), nn.ReLU(inplace=True),
                                  nn.Conv2d(256, 3, 1))

    def forward(self, rgb):
        f8 = self.low(rgb)
        f16 = F.interpolate(self.high(f8), size=f8.shape[-2:], mode="bilinear", align_corners=False)
        return self.head(torch.cat([f8, f16], 1))


def grid_pixels(h, w, scale):
    """Full-resolution pixel (u, v) of each stride-8 cell centre, (h*w, 2)."""
    v, u = np.mgrid[0:h, 0:w]
    return np.stack([(u.ravel() * STRIDE + STRIDE / 2) * scale, (v.ravel() * STRIDE + STRIDE / 2) * scale], 1)


def coord_targets(depth_mm, K, T_world_cam, h, w, scale, dmin, dmax):
    """Room coordinates (mm) of the stride-8 cell centres from the full-resolution depth,
    (h, w, 3), and the valid mask (h, w)."""
    uv = grid_pixels(h, w, scale)
    ui = np.clip(np.round(uv[:, 0]).astype(int), 0, depth_mm.shape[1] - 1)
    vi = np.clip(np.round(uv[:, 1]).astype(int), 0, depth_mm.shape[0] - 1)
    z = depth_mm[vi, ui].astype(np.float64)
    X = np.stack([(uv[:, 0] - K[0, 2]) / K[0, 0] * z, (uv[:, 1] - K[1, 2]) / K[1, 1] * z, z, np.ones_like(z)])
    W = (T_world_cam @ X)[:3].T
    return W.reshape(h, w, 3), ((z > dmin) & (z < dmax)).reshape(h, w)


def load_depth_mm(ds, root, name, row):
    r = ds.runs[name]
    d = cv2.imread(str(Path(root) / name / r["df"]["depth"].iloc[row]), cv2.IMREAD_UNCHANGED)
    return d.astype(np.float32) * r["depth_scale"]


def load_scr(path, device):
    ck = torch.load(path, map_location=device, weights_only=False)
    net = SCRNet(pretrained=False).to(device)
    net.load_state_dict(ck["model"])
    net.eval()
    return net, ck


@torch.no_grad()
def localize(net, ck, rgb, K, full_w, device, px=10.0, min_inliers=30, iters=2000):
    """Camera pose T_world_cam (4x4) of one frame from its predicted room coordinates and
    PnP-RANSAC, or None; also the number of inliers. rgb: (3, H, W) ImageNet-normalised."""
    pred = net(torch.from_numpy(rgb).float()[None].to(device))[0].double().cpu().numpy()
    h, w = pred.shape[1:]
    obj = pred.reshape(3, -1).T * 1000.0 + np.asarray(ck["centre"])
    img = grid_pixels(h, w, full_w / (w * STRIDE))
    found, rvec, tvec, inl = cv2.solvePnPRansac(obj, img, K, None, iterationsCount=iters, reprojectionError=px,
                                                confidence=0.999, flags=cv2.SOLVEPNP_EPNP)
    if not found or inl is None or len(inl) < min_inliers:
        return None, 0 if inl is None else len(inl)
    inl = inl.ravel()
    rvec, tvec = cv2.solvePnPRefineLM(obj[inl], img[inl], K, None, rvec, tvec)
    T_cam_world = np.eye(4)
    T_cam_world[:3, :3], T_cam_world[:3, 3] = cv2.Rodrigues(rvec)[0], tvec.ravel()
    return invert_se3(T_cam_world[None])[0], len(inl)
