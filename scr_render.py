"""
Rendered training views for scr_anchor.py train --render-views (a coverage study, not adopted: 4XX A
5.14 -> 4.98 mm from the voxel cloud, 4.94 mm from real frames; summary.md 4.5).

New viewpoints near the room-scan poses with exact room-coordinate labels, rendered once at the start
of training, from the voxel room cloud (--render-source cloud) or from the nearest real frames at full
resolution (--render-source frames).
"""

import cv2
import numpy as np
import torch
from pathlib import Path
from scipy.spatial.transform import Rotation
from torch.utils.data import Dataset
from tqdm import tqdm

from dataloader import IMAGENET_MEAN, IMAGENET_STD
from scr import STRIDE, load_depth_mm


def bar(it, **kw):
    return tqdm(it, leave=False, dynamic_ncols=True, **kw)


def frame_points(ds, root, name, row, stride, max_depth):
    """One frame as coloured room points: depth back-projected on a `stride`-pixel grid with the frame's pose,
    depth edges dropped -> P (N, 3) mm world, colour (N, 3) uint8, size (N,) mm (the pixel footprint)."""
    r = ds.runs[name]
    rgb = cv2.cvtColor(cv2.imread(str(Path(root) / name / r["df"]["rgb"].iloc[row])), cv2.COLOR_BGR2RGB)
    d = load_depth_mm(ds, root, name, row).astype(np.float32)
    k3 = np.ones((3, 3), np.uint8)
    edge = ((cv2.dilate(d, k3) - cv2.erode(np.where(d > 0, d, np.float32(1e9)), k3)) > 0.03 * d) | \
           (cv2.erode((d > 0).astype(np.uint8), k3) == 0)
    v, u = np.mgrid[0:d.shape[0]:stride, 0:d.shape[1]:stride]
    z = d[v, u].astype(np.float64)
    ok = (z > 100) & (z < max_depth) & ~edge[v, u]
    K, T = np.asarray(r["K"], float), r["T_world_cam"][row]
    X = np.stack([(u[ok] - K[0, 2]) / K[0, 0] * z[ok], (v[ok] - K[1, 2]) / K[1, 1] * z[ok], z[ok]], 1)
    return X @ T[:3, :3].T + T[:3, 3], rgb[v[ok], u[ok]], z[ok] / K[0, 0] * stride


def room_cloud(ds, root, items, every, stride, max_depth, voxel):
    """Coloured point cloud of the room (mm, world frame) from every `every`-th training frame: depth
    back-projected on a `stride`-pixel grid with the frame's pose, depth edges dropped, merged on a
    `voxel`-mm grid (mean position and colour per voxel)."""
    keys, pts, cols = [], [], []

    def merge():
        k = np.concatenate(keys)
        u, inv = np.unique(k, return_inverse=True)
        n = np.bincount(inv).astype(np.float64)[:, None]
        p = np.zeros((len(u), 3))
        c = np.zeros((len(u), 3))
        np.add.at(p, inv, np.concatenate(pts))
        np.add.at(c, inv, np.concatenate(cols))
        keys[:], pts[:], cols[:] = [u], [p / n], [c / n]

    for name, row in bar(items[::every], desc="room cloud"):
        P, col, _ = frame_points(ds, root, name, row, stride, max_depth)
        q = np.floor(P / voxel).astype(np.int64) + (1 << 20)
        keys.append((q[:, 0] << 42) | (q[:, 1] << 21) | q[:, 2])
        pts.append(P)
        cols.append(col.astype(np.float64))
        if len(keys) > 50:
            merge()
    merge()
    return pts[0].astype(np.float32), np.clip(cols[0], 0, 255).astype(np.uint8)


def render_view(P, C, T_wc, K, hw, size, device):
    """Splat the coloured cloud into a camera at T_wc (render resolution hw, intrinsics K); size: the point
    footprint in mm (a voxel size, or a tensor with one per point)
    -> rgb (H, W, 3) uint8, room coordinate (H, W, 3) mm, depth (H, W) mm (0 = nothing)."""
    H, W = hw
    R, t = torch.tensor(T_wc[:3, :3], device=device, dtype=torch.float32), torch.tensor(T_wc[:3, 3], device=device, dtype=torch.float32)
    Xc = (P - t) @ R                                                      # world -> camera
    z = Xc[:, 2]
    m = z > 100
    idx = torch.nonzero(m)[:, 0]
    z = z[m]
    u = Xc[m, 0] / z * K[0, 0] + K[0, 2]
    v = Xc[m, 1] / z * K[1, 1] + K[1, 2]
    sz = size[m] if torch.is_tensor(size) else size
    rad = torch.clamp((sz * K[0, 0] / z * 0.75).round().long(), 0, 2)       # splat half-size: covers the point footprint
    key = (z * 10).long() * (len(P) + 1) + idx                          # nearest wins; ties by index
    best = torch.full((H * W,), torch.iinfo(torch.long).max, device=device, dtype=torch.long)
    ui, vi = u.round().long(), v.round().long()
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            s = (rad >= max(abs(dx), abs(dy)))
            uu, vv = ui[s] + dx, vi[s] + dy
            ok = (uu >= 0) & (uu < W) & (vv >= 0) & (vv < H)
            best.scatter_reduce_(0, (vv[ok] * W + uu[ok]), key[s][ok], reduce="amin")
    hit = best < torch.iinfo(torch.long).max
    src = torch.where(hit, best % (len(P) + 1), torch.zeros_like(best))
    rgb = torch.where(hit[:, None], C[src], torch.zeros_like(C[src])).reshape(H, W, 3)
    xyz = P[src].reshape(H, W, 3)
    dep = torch.where(hit, (best // (len(P) + 1)).float() / 10, torch.zeros_like(best, dtype=torch.float32)).reshape(H, W)
    return rgb.cpu().numpy(), xyz.cpu().numpy(), dep.cpu().numpy()


def perturb(T, shift, rot, rng):
    """The camera pose T moved by up to `shift` mm and turned by up to `rot` deg about its centre (random directions)."""
    a = rng.normal(size=3)
    R = Rotation.from_rotvec(a / np.linalg.norm(a) * np.radians(rng.uniform(0, rot))).as_matrix()
    d = rng.normal(size=3)
    out = T.copy()
    out[:3, :3] = T[:3, :3] @ R
    out[:3, 3] = T[:3, 3] + T[:3, :3] @ (d / np.linalg.norm(d) * rng.uniform(0, shift))
    return out


class RenderedViews(Dataset):
    """New viewpoints rendered with exact room-coordinate labels (rendered once, at the start of
    training): a training pose turned by up to --render-rot and moved by up to --render-shift; kept if
    at least --render-min-valid of its cells have a label. Two sources (--render-source):
      cloud:  the room cloud of every --render-every-th training frame on --render-voxel mm voxels
              (blocky: one colour per voxel);
      frames: the --render-frames training frames nearest to the new pose (camera distance + 28 mm
              per degree of viewing direction), each back-projected at full resolution, so the image
              keeps the real texture.
    Holes are filled from neighbouring pixels in the image only; a cell is labelled only where the
    rendered surface is not seen through a hole (depth within 5 % of its 5 x 5 minimum) and closer
    than the label depth limit. Photometric augmentation as the real frames."""

    def __init__(self, ds, root, items, centre, args, device):
        self.centre, self.seed = np.asarray(centre), args.seed
        frames_mode = args.render_source == "frames"
        if frames_mode:
            Tc = np.stack([ds.runs[n]["T_world_cam"][r] for n, r in items])
            pos, look = Tc[:, :3, 3], Tc[:, :3, 2]
        else:
            P, C = room_cloud(ds, root, items, args.render_every, 4, args.label_max_depth, args.render_voxel)
            print(f"room cloud: {len(P) / 1e6:.2f} M points ({args.render_voxel:g} mm voxels)", flush=True)
            Pt, Ct = torch.from_numpy(P).to(device), torch.from_numpy(C).to(device)
            size = args.render_voxel
        H, W = ds.cfg.image_size
        rng = np.random.default_rng(args.seed + 7)
        n_want = int(round(args.render_views * len(items)))
        self.rgb, self.tgt, self.ok, self.poses = [], [], [], []
        tries = 0
        bar_ = tqdm(total=n_want, desc="rendering views", leave=False)
        while len(self.rgb) < n_want and tries < 20 * n_want:
            tries += 1
            name, row = items[rng.integers(len(items))]
            r = ds.runs[name]
            K = np.asarray(r["K"], float) * np.array([[W / r["hw"][1]], [H / r["hw"][0]], [1]])
            T = perturb(r["T_world_cam"][row], args.render_shift, args.render_rot, rng)
            if frames_mode:                   # the nearest real frames, full resolution
                ang = np.degrees(np.arccos(np.clip(look @ T[:3, 2], -1, 1)))
                near = np.argsort(np.linalg.norm(pos - T[:3, 3], axis=1) + 28.0 * ang)[: args.render_frames]
                parts = [frame_points(ds, root, *items[j], 1, args.label_max_depth) for j in near]
                Pt = torch.from_numpy(np.concatenate([q[0] for q in parts]).astype(np.float32)).to(device)
                Ct = torch.from_numpy(np.concatenate([q[1] for q in parts])).to(device)
                size = torch.from_numpy(np.concatenate([q[2] for q in parts]).astype(np.float32)).to(device)
            rgb, xyz, dep = render_view(Pt, Ct, T, K, (H, W), size, device)
            dmin = cv2.erode(np.where(dep > 0, dep, np.float32(1e9)), np.ones((5, 5), np.uint8))
            ok = (dep > 100) & (dep < args.label_max_depth) & (dep <= 1.05 * dmin)
            o = STRIDE // 2
            okc = ok[o::STRIDE, o::STRIDE]
            if okc.mean() < args.render_min_valid:
                continue
            hole = (dep == 0).astype(np.uint8)
            if hole.any():                                                       # fill holes in the image only
                rgb = cv2.inpaint(rgb, hole, 3, cv2.INPAINT_TELEA)
            self.rgb.append(rgb)
            self.tgt.append(((xyz[o::STRIDE, o::STRIDE] - self.centre) / 1000.0).transpose(2, 0, 1).astype(np.float32))
            self.ok.append(okc)
            self.poses.append(T)
            bar_.update(1)
        bar_.close()
        print(f"{len(self.rgb)} rendered views from {args.render_source} ({tries} tried; shift <= {args.render_shift:g} mm, "
              f"rotation <= {args.render_rot:g} deg)", flush=True)

    def __len__(self):
        return len(self.rgb)

    def __getitem__(self, i):
        rng = np.random.default_rng([self.seed, torch.initial_seed() % 2 ** 32, i, 1])
        b, c, g = rng.uniform(-0.2, 0.2), rng.uniform(0.8, 1.2), rng.uniform(0.9, 1.1, 3)
        rgb = np.clip((self.rgb[i].astype(np.float32) / 255 * g - 0.5) * c + 0.5 + b, 0, 1)
        rgb = ((rgb - IMAGENET_MEAN) / IMAGENET_STD).transpose(2, 0, 1)
        return torch.from_numpy(np.ascontiguousarray(rgb)).float(), torch.from_numpy(self.tgt[i]), torch.from_numpy(self.ok[i])


def render_preview(frames, rendered, path, n=4):
    """A real training frame next to rendered views, for a visual check of the renders."""
    tiles = []
    for k in range(min(n, len(rendered))):
        real = frames.ds.load_frame(*frames.items[(k * 997) % len(frames.items)])[0].transpose(1, 2, 0)
        real = np.clip(real * IMAGENET_STD + IMAGENET_MEAN, 0, 1)
        tiles.append(np.concatenate([(real * 255).astype(np.uint8), rendered.rgb[k * max(1, len(rendered) // n)]], 1))
    cv2.imwrite(str(path), cv2.cvtColor(np.concatenate(tiles, 0), cv2.COLOR_RGB2BGR))
