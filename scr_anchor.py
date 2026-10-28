"""
Scene coordinate regression (SCR) anchors: train a network on a session's room scans, then
localise the camera of each sweep frame.

Network: rgbd-us `scr.py` SCRNet (EfficientNet-B0 to stride 16, stride-8 + stride-16 features,
1x1-conv head) predicting the room coordinate of each cell of a 45 x 80 grid; optionally an
ACE-sized head (--head big). Targets: the room-scan depth at each cell centre, back-projected with
the frame's pose (Polaris, or the system's own estimate with --label-poses).

Training (`train`): every room-scan frame, mean 3D distance loss, AdamW, 120 epochs with a flat
learning rate for 60 % of the steps then a cosine decay to 0, head in fp32 (fp16 would quantise the
output to 1-2 mm). Every --check-every epochs a fit check runs on 120 fixed training frames in eval
mode: coordinate error, the same after the best rigid fit, and the PnP pose of those frames.

Pose (`eval`): --solver kabsch (default): 3D-3D RANSAC between the measured depth of each cell and
its predicted room coordinate; --solver pnp: PnP-RANSAC on the 2D cell centres (rgbd-us scr.py).
Protocol as rgbd-us `scr.py eval`: one frame every 30 usable rows of the test sweeps, camera
position / rotation error against Polaris, with a fixed RANSAC seed per frame.

Checkpoints keep scr.py's format (plus "head"), so tools/anchoring_kabsch.py runs them in the full
system. Data loading and the network come from dataloader.py, geometry.py and scr.py in this repo
(unchanged copies of rgbd-us modules).

  python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/v1-3XX \\
      --eval-root $DATA/train_3XX
  python scr_anchor.py eval --ckpt runs/v1-3XX/best.pt --test-root $DATA/train_3XX
  python scr_anchor.py track --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/track-3XX

Tracking (`track`): the network alone as the tracker, no odometry and no Polaris start pose. SCR +
Kabsch on every --every usable row, poses with fewer than --gate inliers dropped, cached in
<out>/poses.npz; then for each --windows W (s) a robust local fit over time per segment (tricube x
inliers weights, quadratic inside the window's poses, linear with fewer than 5, constant when
extrapolating; 2 Tukey reweightings; rotation as rotation vectors about the window's mean). Error at
the US image as anchoring.py (5 points, median per sweep) and the step-to-step error per --every rows
and per 8 rows (anchoring.py's odometry step).
"""

import argparse
import json
import math
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO))         # dataloader.py, geometry.py, scr.py: copies of rgbd-us

import cv2                                                              # noqa: E402
import numpy as np                                                      # noqa: E402
import torch                                                            # noqa: E402
import torch.nn as nn                                                   # noqa: E402
import torch.nn.functional as F                                         # noqa: E402
from torch.utils.data import ConcatDataset, DataLoader, Dataset          # noqa: E402
from scipy.spatial.transform import Rotation                            # noqa: E402
from tqdm import tqdm                                                   # noqa: E402

from dataloader import IMAGENET_MEAN, IMAGENET_STD, RPRConfig, RPRDataset, load_hand_eye, test_sweeps   # noqa: E402
from scr import STRIDE, SCRNet, coord_targets, grid_pixels, load_depth_mm, localize   # noqa: E402


def bar(it, **kw):
    """Progress bar on stderr; in a log file it refreshes every 10 s so the log stays short."""
    return tqdm(it, mininterval=0.5 if sys.stderr.isatty() else 10, dynamic_ncols=True, leave=False, **kw)


# ---------------------------------------------------------------- network

class SCRNetFP32Head(SCRNet):
    """scr.SCRNet with the head outside autocast. Same parameters, so scr.load_scr loads it."""

    def forward(self, rgb):
        f8 = self.low(rgb)
        f16 = F.interpolate(self.high(f8), size=f8.shape[-2:], mode="bilinear", align_corners=False)
        with torch.autocast(rgb.device.type, enabled=False):
            return self.head(torch.cat([f8, f16], 1).float())


class BigHead(nn.Module):
    """ACE-sized coordinate head (--head big): 1x1 convs, width 512, residual blocks, ~2.2 M
    parameters instead of scr.py's 0.17 M. In SCR the head is the room's memory."""

    def __init__(self, cin=152, width=512, blocks=4):
        super().__init__()
        self.inp = nn.Sequential(nn.Conv2d(cin, width, 1), nn.ReLU(inplace=True))
        self.blocks = nn.ModuleList(nn.Sequential(nn.Conv2d(width, width, 1), nn.ReLU(inplace=True),
                                                  nn.Conv2d(width, width, 1)) for _ in range(blocks))
        self.out = nn.Conv2d(width, 3, 1)

    def forward(self, x):
        x = self.inp(x)
        for b in self.blocks:
            x = torch.relu(x + b(x))
        return self.out(x)


def build_net(head="small", pretrained=True):
    net = SCRNetFP32Head(pretrained=pretrained)
    if head == "big":
        net.head = BigHead()
    return net


def load_model(path, device):
    """scr.load_scr for either head: the checkpoint's "head" entry (absent = scr.py's small head)."""
    ck = torch.load(path, map_location=device, weights_only=False)
    net = build_net(ck.get("head", "small"), pretrained=False).to(device)
    net.load_state_dict(ck["model"])
    net.eval()
    return net, ck


# ---------------------------------------------------------------- training data

class Frames(Dataset):
    """Training frames with their room-coordinate targets.

    The target of cell (u, v) is the room point seen at full-resolution pixel (16u + 8, 16v + 8),
    as in scr.py. Photometric augmentation as scr.RoomScanFrames. Optional:
      * viewpoint augmentation (ACE): a random zoom (log-uniform in `scale`) and in-plane rotation
        (+-`rot` deg) of the image and its room-coordinate map alike; zooming out leaves a border
        without labels;
      * label cleaning: no label beyond `max_depth` (depth noise grows with distance squared) and
        none on depth edges, where a pixel's 3x3 neighbourhood spans more than 3 % of its depth."""

    def __init__(self, ds, root, items, centre, scale=(1.0, 1.0), rot=0.0, max_depth=None, drop_edges=False, seed=0):
        self.ds, self.root, self.items, self.centre = ds, root, items, np.asarray(centre)
        self.log_scale, self.rot = np.log(scale), rot
        self.max_depth, self.drop_edges, self.seed = max_depth, drop_edges, seed

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        rng = np.random.default_rng([self.seed, torch.initial_seed() % 2 ** 32, i])   # differs per worker and epoch
        name, row = self.items[i]
        r, cfg = self.ds.runs[name], self.ds.cfg
        bc = (rng.uniform(-0.2, 0.2), rng.uniform(0.8, 1.2), rng.uniform(0.9, 1.1, 3))
        rgb = np.ascontiguousarray(self.ds.load_frame(name, row, bc)[0].transpose(1, 2, 0))   # (H, W, 3)
        H, W = rgb.shape[:2]

        # room coordinate of every output pixel: full-resolution pixel (f x, f y)
        d = load_depth_mm(self.ds, self.root, name, row)
        K, f = np.asarray(r["K"], float), r["hw"][1] // W
        v, u = np.mgrid[0:H, 0:W] * f
        z = d[v, u].astype(np.float64)
        X = np.stack([(u - K[0, 2]) / K[0, 0] * z, (v - K[1, 2]) / K[1, 1] * z, z])
        T = r["T_world_cam"][row]
        xyz = (np.einsum("ij,jhw->hwi", T[:3, :3], X) + T[:3, 3]).astype(np.float32)
        ok = (z > cfg.min_depth) & (z < min(cfg.max_depth, self.max_depth or np.inf))
        if self.drop_edges:
            df = d.astype(np.float32)
            k = np.ones((3, 3), np.uint8)
            hi = cv2.dilate(df, k)
            lo = cv2.erode(np.where(df > 0, df, np.float32(1e9)), k)
            near_hole = cv2.erode((df > 0).astype(np.uint8), k) == 0           # a missing neighbour counts as an edge
            ok &= ~(near_hole | ((hi - lo) > 0.03 * df))[v, u]
        ok = ok.astype(np.uint8)

        if self.rot > 0 or self.log_scale[0] != self.log_scale[1]:
            M = cv2.getRotationMatrix2D(((W - 1) / 2, (H - 1) / 2), rng.uniform(-self.rot, self.rot),
                                        float(np.exp(rng.uniform(*self.log_scale))))
            rgb = cv2.warpAffine(rgb, M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
            # nearest neighbour for the labels: interpolating across a depth edge invents a surface
            xyz = cv2.warpAffine(xyz, M, (W, H), flags=cv2.INTER_NEAREST)
            ok = cv2.warpAffine(ok, M, (W, H), flags=cv2.INTER_NEAREST, borderValue=0)

        o = STRIDE // 2
        tgt = ((xyz[o::STRIDE, o::STRIDE] - self.centre) / 1000.0).transpose(2, 0, 1)
        return (torch.from_numpy(rgb.transpose(2, 0, 1).copy()).float(), torch.from_numpy(tgt.copy()).float(),
                torch.from_numpy(ok[o::STRIDE, o::STRIDE] > 0))


# ---------------------------------------------------------------- rendered views (--render-views)

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

    for n_item, (name, row) in enumerate(bar(items[::every], desc="room cloud")):
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
        P = X @ T[:3, :3].T + T[:3, 3]
        q = np.floor(P / voxel).astype(np.int64) + (1 << 20)
        keys.append((q[:, 0] << 42) | (q[:, 1] << 21) | q[:, 2])
        pts.append(P)
        cols.append(rgb[v[ok], u[ok]].astype(np.float64))
        if len(keys) > 50:
            merge()
    merge()
    return pts[0].astype(np.float32), np.clip(cols[0], 0, 255).astype(np.uint8)


def render_view(P, C, T_wc, K, hw, voxel, device):
    """Splat the coloured cloud into a camera at T_wc (render resolution hw, intrinsics K):
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
    rad = torch.clamp((voxel * K[0, 0] / z * 0.75).round().long(), 0, 2)    # splat half-size: covers the voxel footprint
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
    """New viewpoints rendered from the room cloud with exact room-coordinate labels (rendered once,
    at the start of training): a training pose turned by up to --render-rot and moved by up to
    --render-shift; kept if at least --render-min-valid of its cells have a label. Holes are filled
    from neighbouring pixels in the image only; a cell is labelled only where the rendered surface
    is not seen through a hole (depth within 5 % of its 5 x 5 minimum) and closer than the label
    depth limit. Photometric augmentation as the real frames."""

    def __init__(self, ds, root, items, centre, args, device):
        self.centre, self.seed = np.asarray(centre), args.seed
        P, C = room_cloud(ds, root, items, args.render_every, 4, args.label_max_depth, args.render_voxel)
        print(f"room cloud: {len(P) / 1e6:.2f} M points ({args.render_voxel:g} mm voxels)", flush=True)
        Pt, Ct = torch.from_numpy(P).to(device), torch.from_numpy(C).to(device)
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
            rgb, xyz, dep = render_view(Pt, Ct, T, K, (H, W), args.render_voxel, device)
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
        print(f"{len(self.rgb)} rendered views ({tries} tried; shift <= {args.render_shift:g} mm, rotation <= "
              f"{args.render_rot:g} deg)", flush=True)

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


def label_with_estimates(ds, paths):
    """Map extension without a tracker: the runs exported in these poses.py JSON files (the
    system's own trajectory, T_world_cam_pred) are labelled with that estimate instead of the
    Polaris pose; their rows without an estimate get NaN and are dropped from training. Returns,
    per run, how far the estimated labels are from Polaris (for the record only)."""
    err = {}
    for p in paths:
        d = json.load(open(p))
        run = d["run"]
        if run not in ds.runs:
            raise SystemExit(f"{p}: {run} is not in --scan-runs")
        rows = np.array([f["row"] for f in d["frames"]])
        T = np.array([f["T_world_cam_pred"] for f in d["frames"]])
        T_gt = ds.runs[run]["T_world_cam"][rows]
        dt = np.linalg.norm(T[:, :3, 3] - T_gt[:, :3, 3], axis=1)
        dR = np.einsum("nji,njk->nik", T[:, :3, :3], T_gt[:, :3, :3])
        dr = np.degrees(np.arccos(np.clip((np.trace(dR, axis1=1, axis2=2) - 1) / 2, -1, 1)))
        est = np.full_like(ds.runs[run]["T_world_cam"], np.nan)
        est[rows] = T
        ds.runs[run]["T_world_cam"] = est
        err[run] = {"source": d["source"], "frames": len(rows), "camera_err_mm_median": float(np.median(dt)),
                    "camera_err_mm_p90": float(np.percentile(dt, 90)), "rot_err_deg_median": float(np.median(dr))}
        print(f"  {run}: labelled with {d['source']} ({len(rows)} frames; vs Polaris {err[run]['camera_err_mm_median']:.1f} mm "
              f"median, p90 {err[run]['camera_err_mm_p90']:.1f} mm, {err[run]['rot_err_deg_median']:.2f} deg)", flush=True)
    return err


# ---------------------------------------------------------------- pose

def kabsch(P, Q):
    """R, t minimising |R P + t - Q|, P and Q (N, 3)."""
    cp, cq = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - cp).T @ (Q - cq))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, cq - R @ cp


@torch.no_grad()
def cell_correspondences(net, ck, rgb, depth_mm, K, full_w, device, max_depth=2000.0):
    """(C, P), each (N, 3) mm: for every cell with measured depth below `max_depth`, its depth
    point in the camera frame (C) and its predicted room coordinate (P). Cells beyond max_depth are
    left out: depth noise grows with distance squared."""
    pred = net(torch.from_numpy(rgb).float()[None].to(device))[0].double().cpu().numpy()
    h, w = pred.shape[1:]
    P = pred.reshape(3, -1).T * 1000.0 + np.asarray(ck["centre"])
    uv = grid_pixels(h, w, full_w / (w * STRIDE))
    ui = np.clip(np.round(uv[:, 0]).astype(int), 0, depth_mm.shape[1] - 1)
    vi = np.clip(np.round(uv[:, 1]).astype(int), 0, depth_mm.shape[0] - 1)
    z = depth_mm[vi, ui].astype(np.float64)
    m = (z > 100) & (z < max_depth)
    C = np.stack([(uv[:, 0] - K[0, 2]) / K[0, 0] * z, (uv[:, 1] - K[1, 2]) / K[1, 1] * z, z], 1)[m]
    return C, P[m]


def localize_kabsch(net, ck, rgb, depth_mm, K, full_w, device, thr=20.0, max_depth=2000.0, min_inliers=30,
                    iters=256, rng=None):
    """Camera pose T_world_cam of one frame: Kabsch RANSAC (kabsch_ransac) on its cell correspondences."""
    C, P = cell_correspondences(net, ck, rgb, depth_mm, K, full_w, device, max_depth)
    return kabsch_ransac(C, P, thr, min_inliers, iters, rng)


def kabsch_ransac(C, P, thr=20.0, min_inliers=30, iters=256, rng=None):
    """T (4x4) mapping camera points C onto room points P, by RANSAC: hypotheses from 3 random
    correspondences (Kabsch), inliers within `thr` mm, refit three times on the inliers.
    Returns (T or None, number of inliers)."""
    if len(P) < max(min_inliers, 3):
        return None, 0
    rng = rng or np.random.default_rng(0)
    idx = rng.integers(0, len(P), (iters, 3))
    Cs, Ps = C[idx], P[idx]                                                # (iters, 3, 3)
    cc, cp = Cs.mean(1, keepdims=True), Ps.mean(1, keepdims=True)
    U, _, Vt = np.linalg.svd(np.swapaxes(Cs - cc, 1, 2) @ (Ps - cp))
    D = np.sign(np.linalg.det(np.swapaxes(Vt, 1, 2) @ np.swapaxes(U, 1, 2)))
    Vt[:, 2] *= D[:, None]                                                 # no reflections
    R = np.swapaxes(Vt, 1, 2) @ np.swapaxes(U, 1, 2)
    t = cp[:, 0] - np.einsum("kij,kj->ki", R, cc[:, 0])
    n_in = (np.linalg.norm(np.einsum("kij,nj->kni", R, C) + t[:, None] - P, axis=2) < thr).sum(1)
    R, t = R[n_in.argmax()], t[n_in.argmax()]
    for _ in range(3):                                                     # refit on the inliers
        inl = np.linalg.norm(C @ R.T + t - P, axis=1) < thr
        if inl.sum() < max(min_inliers, 3):
            return None, int(inl.sum())
        R, t = kabsch(C[inl], P[inl])
    T = np.eye(4)
    T[:3, :3], T[:3, 3] = R, t
    return T, int((np.linalg.norm(C @ R.T + t - P, axis=1) < thr).sum())


def pose_err(T, T_gt):
    dR = T[:3, :3].T @ T_gt[:3, :3]
    return (float(np.linalg.norm(T[:3, 3] - T_gt[:3, 3])),
            float(np.degrees(np.arccos(np.clip((np.trace(dR) - 1) / 2, -1, 1)))))


# ---------------------------------------------------------------- helpers

def flatcos(total, warmup, flat):
    """LR factor: linear warm-up, constant until `flat` of the steps, cosine to 0."""
    def f(s):
        if s < warmup:
            return (s + 1) / warmup
        if s < flat * total:
            return 1.0
        return 0.5 * (1 + math.cos(math.pi * (s - flat * total) / max(total - flat * total, 1)))
    return f


def git_rev(path):
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def resolve_hand_eye(path):
    """The hand-eye file a checkpoint names; if that path does not exist on this computer (a
    checkpoint trained elsewhere), this repo's T_marker_cam.npy."""
    p = Path(path)
    return str(p.resolve() if p.exists() else REPO / "T_marker_cam.npy")


@torch.no_grad()
def fit_check(net, ck, ds, root, items, device, args):
    """Eval-mode fp32 fit on training frames: coordinate error per frame (median over cells),
    the same after the best rigid fit, and the PnP pose error of the frames themselves."""
    net.eval()
    H, W = ds.cfg.image_size
    h, w = H // STRIDE, W // STRIDE
    coord, resid, t_err, r_err, solved = [], [], [], [], 0
    for name, row in bar(items, desc="fit check"):
        r = ds.runs[name]
        K = np.asarray(r["K"], float)
        rgb = ds.load_frame(name, row)[0]
        tgt, ok = coord_targets(load_depth_mm(ds, root, name, row), K, r["T_world_cam"][row], h, w,
                                r["hw"][1] / W, ds.cfg.min_depth, ds.cfg.max_depth)
        pred = net(torch.from_numpy(rgb).float()[None].to(device))[0].double().cpu().numpy()
        P = pred.reshape(3, -1).T * 1000.0 + np.asarray(ck["centre"])
        m = ok.ravel()
        if m.sum() < 6:
            continue
        P, Q = P[m], tgt.reshape(-1, 3)[m]
        coord.append(np.median(np.linalg.norm(P - Q, axis=1)))
        R, t = kabsch(P, Q)
        resid.append(np.median(np.linalg.norm(P @ R.T + t - Q, axis=1)))
        cv2.setRNGSeed(args.seed + int(row))
        T, _ = localize(net, ck, rgb, K, r["hw"][1], device, args.px, args.min_inliers)
        if T is not None:
            solved += 1
            dt, dr = pose_err(T, r["T_world_cam"][row])
            t_err.append(dt)
            r_err.append(dr)
    net.train()
    med = lambda v: float(np.median(v)) if len(v) else None
    return {"frames": len(coord), "coord_mm": med(coord), "coord_after_rigid_mm": med(resid),
            "pose_mm": med(t_err), "pose_deg": med(r_err), "solved_pct": 100 * solved / max(len(coord), 1)}


# ---------------------------------------------------------------- train

def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)
    args.hand_eye = resolve_hand_eye(args.hand_eye)
    cfg = RPRConfig(T_marker_cam=load_hand_eye(args.hand_eye, "mm"), image_size=tuple(args.image_size))
    ds = RPRDataset(args.root, args.scan_runs, args.scan_runs, cfg)
    label_err = label_with_estimates(ds, args.label_poses)
    items = [(n, int(r)) for n in args.scan_runs for r in np.concatenate(ds.runs[n]["segments"])
             if np.isfinite(ds.runs[n]["T_world_cam"][r]).all()]
    if args.max_frames:                     # smoke tests only
        items = items[:: max(1, len(items) // args.max_frames)][: args.max_frames]
    centre = np.mean([ds.runs[n]["T_world_cam"][r][:3, 3] for n, r in items], 0)
    check_items = [items[i] for i in np.linspace(0, len(items) - 1, min(args.check_frames, len(items))).astype(int)]
    print(f"{len(items)} training frames from {', '.join(args.scan_runs)}; scene centre {np.round(centre).tolist()} mm; "
          f"fit check on {len(check_items)} of them", flush=True)

    frames = Frames(ds, args.root, items, centre, args.aug_scale, args.aug_rot, args.label_max_depth,
                    args.drop_depth_edges, args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    data, n_rendered = frames, 0
    if args.render_views > 0:                 # extra viewpoints rendered from the room cloud, exact labels
        rendered = RenderedViews(ds, args.root, items, centre, args, device)
        render_preview(frames, rendered, out / "render_preview.jpg")
        data, n_rendered = ConcatDataset([frames, rendered]), len(rendered)
    # decoding two 1280 x 720 PNGs per sample, not the network, limits the speed
    dl = DataLoader(data, args.batch_size, shuffle=True, num_workers=args.workers, drop_last=True,
                    pin_memory=device.type == "cuda", persistent_workers=args.workers > 0,
                    prefetch_factor=4 if args.workers > 0 else None)
    net = build_net(args.head).to(device)
    encoder = list(net.low.parameters()) + list(net.high.parameters())
    if args.freeze_encoder:                   # ACE-style: ImageNet features as they are, only the head learns
        for q in encoder:
            q.requires_grad_(False)
    opt = torch.optim.AdamW([{"params": encoder, "lr": 0.0 if args.freeze_encoder else args.lr_encoder},
                             {"params": net.head.parameters(), "lr": args.lr}], weight_decay=1e-4)
    total = args.epochs * len(dl)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, flatcos(total, max(1, total // 100), args.flat))
    amp = device.type == "cuda"
    scaler = torch.amp.GradScaler(enabled=amp)

    meta = {"args": vars(args), "centre": centre.tolist(), "image_size": list(args.image_size), "head": args.head}
    json.dump(meta | {"n_frames": len(items), "n_rendered": n_rendered, "steps": total, "estimated_labels": label_err, "git": git_rev(REPO)},
              open(out / "config.json", "w"), indent=2)
    print(f"{len(dl)} steps per epoch, {total} in all; head {args.head} "
          f"({sum(p.numel() for p in net.head.parameters()) / 1e6:.2f} M); labels < {args.label_max_depth:g} mm"
          f"{', no depth edges' if args.drop_depth_edges else ''}; viewpoint augmentation "
          f"{f'zoom {args.aug_scale}, rotation +-{args.aug_rot} deg' if args.aug_rot or args.aug_scale != [1.0, 1.0] else 'off'}"
          f"{f'; + {n_rendered} rendered views' if n_rendered else ''}{'; encoder frozen' if args.freeze_encoder else ''}",
          flush=True)

    history = []
    for ep in range(args.epochs):
        net.train()
        if args.freeze_encoder:               # keep the ImageNet batch-norm statistics too
            net.low.eval()
            net.high.eval()
        t0, losses, meds = time.time(), [], []
        pbar = bar(dl, desc=f"epoch {ep + 1}/{args.epochs}")
        for rgb, tgt, ok in pbar:
            rgb, tgt, ok = (x.to(device, non_blocking=True) for x in (rgb, tgt, ok))
            with torch.autocast(device.type, enabled=amp):
                pred = net(rgb)
            err = torch.linalg.norm(pred.float() - tgt, dim=1)[ok]               # 3D distance, metres
            if err.numel() == 0:
                continue
            loss = err.mean()
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            losses.append(loss.item())
            meds.append(float(err.detach().median()) * 1000)
            pbar.set_postfix(loss=f"{losses[-1]:.4f}", err=f"{meds[-1]:.0f} mm", refresh=False)
        h = {"epoch": ep + 1, "loss": float(np.mean(losses)), "coord_err_mm_median": float(np.median(meds)),
             "lr_head": opt.param_groups[1]["lr"], "epoch_s": round(time.time() - t0)}
        line = (f"epoch {ep + 1}/{args.epochs}: loss {h['loss']:.4f}, train-mode coordinate error "
                f"{h['coord_err_mm_median']:.1f} mm, lr {h['lr_head']:.1e}, {h['epoch_s']} s")
        torch.save({"model": net.state_dict(), "epoch": ep, **meta}, out / "best.pt")
        if (ep + 1) % args.check_every == 0 or ep + 1 == args.epochs:
            h["fit"] = fit_check(net, meta, ds, args.root, check_items, device, args)
            f = h["fit"]
            fmt = lambda v, d=1: "-" if v is None else f"{v:.{d}f}"
            line += (f" | fit check: coordinates {fmt(f['coord_mm'])} mm ({fmt(f['coord_after_rigid_mm'])} after "
                     f"rigid fit), pose {fmt(f['pose_mm'])} mm / {fmt(f['pose_deg'], 2)} deg, "
                     f"{f['solved_pct']:.0f} % solved")
        print(line, flush=True)
        history.append(h)
        json.dump(history, open(out / "history.json", "w"), indent=2)
    print(f"done -> {out / 'best.pt'}", flush=True)

    if args.eval_root:
        evaluate(argparse.Namespace(ckpt=str(out / "best.pt"), test_root=args.eval_root, test_runs=args.eval_runs,
                                    every=30, solver="kabsch", px=args.px, min_inliers=args.min_inliers,
                                    kabsch_thr=20.0, kabsch_max_depth=2000.0, seed=args.seed, out=None))


# ---------------------------------------------------------------- evaluate

def evaluate(args):
    """One frame every --every usable rows of the test sweeps; pose by Kabsch or PnP; error against Polaris."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net, ck = load_model(args.ckpt, device)
    cfg = RPRConfig(T_marker_cam=load_hand_eye(resolve_hand_eye(ck["args"]["hand_eye"]), "mm"),
                    image_size=tuple(ck["image_size"]))
    sweeps = test_sweeps(args.test_root, args.test_runs)
    ds = RPRDataset(args.test_root, sweeps, [], cfg)
    rows, per = [], {}
    for sw in sweeps:
        r = ds.runs[sw]
        K = np.asarray(r["K"], float)
        for row in bar(np.concatenate(r["segments"])[:: args.every], desc=f"eval {sw}"):
            rgb = ds.load_frame(sw, int(row))[0]
            if args.solver == "kabsch":
                depth = load_depth_mm(ds, args.test_root, sw, int(row))
                t0 = time.perf_counter()
                T, n_inl = localize_kabsch(net, ck, rgb, depth, K, r["hw"][1], device, args.kabsch_thr,
                                           args.kabsch_max_depth, args.min_inliers,
                                           rng=np.random.default_rng(args.seed + int(row)))
            else:
                cv2.setRNGSeed(args.seed + int(row))
                t0 = time.perf_counter()
                T, n_inl = localize(net, ck, rgb, K, r["hw"][1], device, args.px, args.min_inliers)
            ms = 1000 * (time.perf_counter() - t0)
            rec = {"run": sw, "row": int(row), "solved": T is not None, "inliers": n_inl, "ms": ms}
            if T is not None:
                rec["err_mm"], rec["err_deg"] = pose_err(T, r["T_world_cam"][row])
            rows.append(rec)
        per[sw] = summary([x for x in rows if x["run"] == sw])
        p = per[sw]
        g = lambda v, d=1: "-" if v is None else f"{v:.{d}f}"
        print(f"  {sw}: {p['frames']} frames, {p['solved_pct']:.0f} % solved, error median {g(p['err_mm_median'])} mm "
              f"(p90 {g(p['err_mm_p90'])}), {g(p['err_deg_median'], 2)} deg", flush=True)
    allp = summary(rows)
    sw_med = [p["err_mm_median"] for p in per.values() if p["err_mm_median"] is not None]
    allp["err_mm_mean_of_sweep_medians"] = float(np.mean(sw_med)) if sw_med else None

    tag = (Path(args.test_root).name + ("_" + "+".join(args.test_runs) if args.test_runs else "")
           + ("_kabsch" if args.solver == "kabsch" else ""))
    solver = (f"Kabsch RANSAC on the measured depth ({args.kabsch_thr:g} mm, cells < {args.kabsch_max_depth:g} mm"
              if args.solver == "kabsch" else f"PnP-RANSAC ({args.px:g} px")
    out = Path(args.out or Path(args.ckpt).parent / f"eval_{tag}")
    out.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(args), "all": allp, "per_sweep": per, "frames": rows}, open(out / "scr_eval.json", "w"),
              indent=1)
    f = lambda v, d=1: "–" if v is None else f"{v:.{d}f}"
    md = [f"# SCR anchors: {Path(args.ckpt).parent.name} on {tag}", "",
          f"One frame every {args.every} usable rows; {solver}, >= {args.min_inliers} inliers, "
          f"seed {args.seed} + row); camera position / rotation error against Polaris.", "",
          "| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |",
          "|---|---|---|---|---|---|---|"]
    md += [f"| {sw} | {p['frames']} | {p['solved_pct']:.0f} % | {f(p['err_mm_median'])} / {f(p['err_mm_p90'])} | "
           f"{f(p['err_deg_median'], 2)} / {f(p['err_deg_p90'], 2)} | {p['inliers_median']:.0f} | {p['ms_median']:.0f} |"
           for sw, p in per.items()]
    md.append(f"| **all (pooled)** | {allp['frames']} | {allp['solved_pct']:.0f} % | {f(allp['err_mm_median'])} / "
              f"{f(allp['err_mm_p90'])} | {f(allp['err_deg_median'], 2)} / {f(allp['err_deg_p90'], 2)} | "
              f"{allp['inliers_median']:.0f} | {allp['ms_median']:.0f} |")
    md.append(f"| **mean of sweep medians** | | | {f(allp['err_mm_mean_of_sweep_medians'])} | | | |")
    (out / "scr_eval.md").write_text("\n".join(md) + "\n")
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'scr_eval.md'}", flush=True)


def summary(rows):
    ok = [x for x in rows if x["solved"]]
    q = lambda k, p: float(np.percentile([x[k] for x in ok], p)) if ok else None
    return {"frames": len(rows), "solved_pct": 100 * len(ok) / max(len(rows), 1),
            "err_mm_median": q("err_mm", 50), "err_mm_p90": q("err_mm", 90),
            "err_deg_median": q("err_deg", 50), "err_deg_p90": q("err_deg", 90),
            "inliers_median": float(np.median([x["inliers"] for x in rows])) if rows else 0.0,
            "ms_median": float(np.median([x["ms"] for x in rows])) if rows else 0.0}


# ---------------------------------------------------------------- track: the network alone on every frame

US_PX = np.array([[320, 240], [160, 120], [480, 120], [160, 400], [480, 400]], float)   # anchoring.py us_points


def read_us_calib(path):
    """calib_matrix.csv (TUS-REC format) -> (scaling, rigid): pixels -> US mm -> marker mm."""
    rows = [l.strip().split(",") for l in open(path)]
    return np.array(rows[1:5], float), np.array(rows[6:10], float)


def track_poses(args, ds, sweeps, net, ck, device):
    """{sweep: (rows, T (n, 4, 4) or NaN, inliers)} for every --every usable row."""
    out = {}
    for sw in sweeps:
        r = ds.runs[sw]
        K = np.asarray(r["K"], float)
        rows = np.concatenate(r["segments"])[:: args.every]
        T = np.full((len(rows), 4, 4), np.nan)
        inl = np.zeros(len(rows), int)
        for n, row in enumerate(bar(rows, desc=f"track {sw}")):
            rgb = ds.load_frame(sw, int(row))[0]
            depth = load_depth_mm(ds, args.test_root, sw, int(row))
            Tn, k = localize_kabsch(net, ck, rgb, depth, K, r["hw"][1], device, rng=np.random.default_rng(int(row)))
            inl[n] = k
            if Tn is not None and k >= args.gate:
                T[n] = Tn
        out[sw] = (rows, T, inl)
        print(f"  {sw}: {len(rows)} frames, {np.isfinite(T[:, 0, 0]).mean() * 100:.0f} % passed the gate", flush=True)
    return out


def smooth_poses(t, T, w, W):
    """Robust local fit of the poses T (n, 4, 4; NaN = none) at times t, weights w, window W (s): quadratic in
    time inside the poses of the window, linear with fewer than 5, constant when extrapolating (gaps, ends)."""
    ok = np.isfinite(T[:, 0, 0])
    if ok.sum() < 3:
        return np.full_like(T, np.nan)
    tt, TT, ww = t[ok], T[ok], w[ok].astype(float)
    out = np.full_like(T, np.nan)
    for i in range(len(t)):
        m = np.abs(tt - t[i]) <= W / 2
        if m.sum() < 3:                                          # gap: widen to the 3 nearest poses
            m = np.zeros(len(tt), bool)
            m[np.argsort(np.abs(tt - t[i]))[:3]] = True
        dt = tt[m] - t[i]
        k = (1 - np.clip(np.abs(dt) / max(W / 2, np.abs(dt).max() + 1e-6), 0, 1) ** 3) ** 3 * ww[m]
        inside = dt.min() < 0 < dt.max()                          # interpolating, not extrapolating
        order = 2 if (m.sum() >= 5 and inside) else 1 if (m.sum() >= 3 and inside) else 0
        A = np.vander(dt, order + 1, increasing=True)
        Rm = Rotation.from_matrix(TT[m, :3, :3])
        rob = np.ones(m.sum())
        for _ in range(3):                                       # fit, then 2 Tukey reweightings
            kw = k * rob + 1e-12
            Rref = Rm.mean(weights=kw)
            Y = np.column_stack([TT[m, :3, 3], (Rref.inv() * Rm).as_rotvec() * 1000.0])   # mm, mrad
            sw = np.sqrt(kw)[:, None]
            coef = np.linalg.lstsq(A * sw, Y * sw, rcond=None)[0]
            res = np.linalg.norm((A @ coef - Y)[:, :3], axis=1) + np.linalg.norm((A @ coef - Y)[:, 3:], axis=1) * 0.16
            s = 6 * np.median(res) + 1e-6
            rob = np.clip(1 - (res / s) ** 2, 0, 1) ** 2
        out[i] = np.eye(4)
        out[i, :3, 3] = coef[0, :3]
        out[i, :3, :3] = (Rref * Rotation.from_rotvec(coef[0, 3:] / 1000.0)).as_matrix()
    return out


def us_errors(T, T_gt, P, segs, steps=(1, 8)):
    """US-image error per frame (mean over the 5 points) and mean step-to-step error for each step size."""
    D = (T @ P - T_gt @ P)[:, :3]                                # (n, 3, 5)
    err = np.linalg.norm(D, axis=1).mean(1)
    st = {}
    for k in steps:
        d = [np.linalg.norm(D[a + k] - D[a], axis=0).mean() for s in segs for a in s[:-k]
             if np.isfinite(D[a]).all() and np.isfinite(D[a + k]).all()]
        st[k] = float(np.mean(d)) if d else float("nan")
    return err, st


def track(args):
    """Single-model tracking: SCR + Kabsch on every --every usable row (no odometry, no Polaris start pose),
    gate, cache the poses; smooth them for each --windows W; error at the US image (as anchoring.py)."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net, ck = load_model(args.ckpt, device)
    T_mc = load_hand_eye(resolve_hand_eye(ck["args"]["hand_eye"]), "mm")
    ds = RPRDataset(args.test_root, test_sweeps(args.test_root, args.test_runs), [],
                    RPRConfig(T_marker_cam=T_mc, image_size=tuple(ck["image_size"])))
    sweeps = list(ds.runs)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "poses.npz"
    if cache.exists() and json.load(open(out / "poses.json"))["every"] == args.every:
        z = np.load(cache)
        raw = {sw: (z[f"{sw}_rows"], z[f"{sw}_T"], z[f"{sw}_inl"]) for sw in sweeps}
        print(f"poses from {cache}")
    else:
        raw = track_poses(args, ds, sweeps, net, ck, device)
        np.savez_compressed(cache, **{f"{sw}_{k}": v for sw, (r, T, i) in raw.items() for k, v in (("rows", r), ("T", T), ("inl", i))})
        json.dump({"ckpt": args.ckpt, "every": args.every, "gate": args.gate}, open(out / "poses.json", "w"))

    scaling, rigid = read_us_calib(args.calib)
    P = np.linalg.inv(T_mc) @ rigid @ scaling @ np.stack([US_PX[:, 0], US_PX[:, 1], np.zeros(5), np.ones(5)])
    methods = ["raw"] + [f"smoothed {W:g} s" for W in args.windows]
    res = {m: {} for m in methods}
    for sw in sweeps:
        rows, T, inl = raw[sw]
        r = ds.runs[sw]
        seg_of = {int(x): k for k, s in enumerate(r["segments"]) for x in s}
        segs = [np.flatnonzero(np.array([seg_of[int(x)] for x in rows]) == k) for k in range(len(r["segments"]))]
        segs = [s for s in segs if len(s) > 1]
        T_gt = r["T_world_cam"][rows]
        t = r["stamps"][rows]
        ests = {"raw": T}
        for W in args.windows:
            Ts = np.full_like(T, np.nan)
            for s in segs:
                Ts[s] = smooth_poses(t[s], T[s], inl[s], W)
            ests[f"smoothed {W:g} s"] = Ts
        step8 = max(1, round(8 / args.every))
        for m, Te in ests.items():
            err, st = us_errors(Te, T_gt, P, segs, steps=(1, step8))
            res[m][sw] = {"us_median": float(np.nanmedian(err)), "us_p90": float(np.nanpercentile(err, 90)),
                          "coverage_pct": float(100 * np.isfinite(err).mean()), "step_row": st[1], "step_8rows": st[step8]}

    mean = lambda m, k: float(np.nanmean([v[k] for v in res[m].values()]))
    md = [f"# Single-model tracking: SCR alone on every {'' if args.every == 1 else f'{args.every}th '}row "
          f"({Path(args.test_root).name}, `{args.ckpt}`)", "",
          f"No odometry, no Polaris start pose; Kabsch RANSAC, gate >= {args.gate} inliers. Error at the US image (5 points, "
          "mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows "
          f"({args.every} row(s), {args.every * 33} ms) and 8 rows (anchoring.py's odometry step).", "",
          f"| method | US image median | p90 | frames with a pose | step, {args.every} row(s) | step, 8 rows |", "|---|---|---|---|---|---|"]
    for m in methods:
        md.append(f"| {m} | **{mean(m, 'us_median'):.2f}** | {mean(m, 'us_p90'):.2f} | {mean(m, 'coverage_pct'):.0f} % | "
                  f"{mean(m, 'step_row'):.3f} | {mean(m, 'step_8rows'):.2f} |")
    md += ["", "Per sweep (US image median, step 8 rows):", "", "| sweep | " + " | ".join(methods) + " |",
           "|---|" + "---|" * len(methods)]
    for sw in sweeps:
        md.append(f"| {sw} | " + " | ".join(f"{res[m][sw]['us_median']:.1f} ({res[m][sw]['step_8rows']:.2f})" for m in methods) + " |")
    (out / "scr_track.md").write_text("\n".join(md) + "\n")
    json.dump({"args": vars(args), "per_sweep": res}, open(out / "scr_track.json", "w"), indent=1)
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'scr_track.md'}")



def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--root", required=True, help="collection folder, e.g. $DATA/train_3XX")
    t.add_argument("--scan-runs", nargs="+", required=True, help="room scans (and extra sweeps) to train on")
    t.add_argument("--out", required=True)
    t.add_argument("--label-poses", nargs="+", default=[],
                   help="poses.py JSON exports: label these --scan-runs with the system's estimated poses "
                        "(T_world_cam_pred) instead of Polaris (map extension without a tracker)")
    t.add_argument("--head", choices=["small", "big"], default="small", help="small: scr.py's 0.17 M head; big: ~2.2 M")
    t.add_argument("--label-max-depth", type=float, default=3000.0, help="no training label beyond this depth (mm)")
    t.add_argument("--drop-depth-edges", action="store_true", help="no training label on depth edges")
    t.add_argument("--freeze-encoder", action="store_true", help="train the head only on frozen ImageNet features (ACE-style)")
    t.add_argument("--render-views", type=float, default=0.0,
                   help="add this many rendered views per training frame (e.g. 0.5), new viewpoints from the room cloud")
    t.add_argument("--render-shift", type=float, default=150.0, help="rendered views: camera moved by up to this (mm)")
    t.add_argument("--render-rot", type=float, default=20.0, help="rendered views: camera turned by up to this (deg)")
    t.add_argument("--render-voxel", type=float, default=5.0, help="room cloud voxel size (mm)")
    t.add_argument("--render-every", type=int, default=4, help="room cloud from every n-th training frame")
    t.add_argument("--render-min-valid", type=float, default=0.5, help="keep a rendered view if this share of cells has a label")
    t.add_argument("--aug-scale", type=float, nargs=2, default=[1.0, 1.0],
                   help="viewpoint augmentation: zoom range, log-uniform (ACE: 0.67 1.5); 1 1 = off")
    t.add_argument("--aug-rot", type=float, default=0.0, help="viewpoint augmentation: in-plane rotation +- deg (ACE: 15)")
    t.add_argument("--epochs", type=int, default=120)
    t.add_argument("--flat", type=float, default=0.6, help="share of the steps at full learning rate")
    t.add_argument("--batch-size", type=int, default=8)
    t.add_argument("--lr", type=float, default=1e-3, help="head")
    t.add_argument("--lr-encoder", type=float, default=1e-4)
    t.add_argument("--image-size", type=int, nargs=2, default=[360, 640])
    t.add_argument("--hand-eye", default=str(REPO / "T_marker_cam.npy"))
    t.add_argument("--workers", type=int, default=12)
    t.add_argument("--seed", type=int, default=0)
    t.add_argument("--check-every", type=int, default=6, help="epochs between fit checks")
    t.add_argument("--check-frames", type=int, default=120)
    t.add_argument("--max-frames", type=int, default=0, help="smoke tests only: cap the training frames")
    t.add_argument("--px", type=float, default=10.0, help="fit check: PnP threshold (px)")
    t.add_argument("--min-inliers", type=int, default=30)
    t.add_argument("--eval-root", default=None, help="evaluate (Kabsch) on these sweeps after training")
    t.add_argument("--eval-runs", nargs="+", default=None)
    e = sub.add_parser("eval")
    e.add_argument("--ckpt", required=True)
    e.add_argument("--test-root", required=True)
    e.add_argument("--test-runs", nargs="+", default=None, help="default: every run-* in --test-root")
    e.add_argument("--solver", choices=["kabsch", "pnp"], default="kabsch",
                   help="kabsch: 3D-3D RANSAC with the measured depth; pnp: PnP-RANSAC on the cell centres (scr.py)")
    e.add_argument("--kabsch-thr", type=float, default=20.0, help="kabsch: inlier threshold (mm)")
    e.add_argument("--kabsch-max-depth", type=float, default=2000.0, help="kabsch: leave out cells farther than this (mm)")
    e.add_argument("--px", type=float, default=10.0, help="pnp: reprojection threshold (px, full resolution)")
    e.add_argument("--min-inliers", type=int, default=30)
    e.add_argument("--every", type=int, default=30, help="usable rows between evaluated frames (30 = 1 s)")
    e.add_argument("--seed", type=int, default=0)
    e.add_argument("--out", default=None)
    k = sub.add_parser("track", help="the network alone on every frame + temporal smoothing")
    k.add_argument("--ckpt", required=True)
    k.add_argument("--test-root", required=True)
    k.add_argument("--test-runs", nargs="+", default=None)
    k.add_argument("--every", type=int, default=1, help="SCR on every n-th usable row")
    k.add_argument("--gate", type=int, default=400, help="minimum Kabsch inliers (as the full system)")
    k.add_argument("--windows", type=float, nargs="+", default=[0.25, 0.5, 1.0, 2.0], help="smoothing windows (s)")
    k.add_argument("--calib", default=str(REPO / "calib_matrix.csv"), help="US calibration (TUS-REC format)")
    k.add_argument("--out", required=True)
    args = ap.parse_args()
    {"train": train, "eval": evaluate, "track": track}[args.cmd](args)


if __name__ == "__main__":
    main()
