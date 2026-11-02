"""
Scene coordinate regression (SCR) for probe tracking: train one network on a room's scans, then give
the camera pose of every sweep frame. Commands: train, eval, track (and scr_map.py builds the map).

Final pipeline (summary.md 2.2, 3.1):
  train  every room-scan frame; label of each of the 45 x 80 cells = its depth point (0.1-2 m, not on a
         depth edge) placed in the room with the frame's pose (Polaris, or --label-poses: estimated poses
         in poses.py JSON, e.g. from scr_map.py); network: EfficientNet-B0 stride-8 + stride-16 features
         -> 1x1 head (big: 4 residual blocks, 512); loss: mean 3D distance; AdamW, 120 epochs, flat lr
         for 60 % then cosine; photometric augmentation. The defaults are this recipe (v2).
  track  every --every-th usable row: network -> room coordinates; Kabsch RANSAC with the measured depth
         (256 hypotheses, 20 mm, 3 refits, >= --gate inliers); robust local fit over time per segment for
         each --windows W (offline) and, with --lags L, in real time (last W s up to t + L, extrapolated
         linearly to t; L = 0 causal). Error at the US image (5 points, median per sweep) and step-to-step
         error per --every rows and per 8 rows. Raw poses cached in <out>/poses.npz; with the cache the
         smoothing reruns on the CPU without the checkpoint. --cam-calib <map.json>: network trained on
         scr_map.py labels; every pose is multiplied by the map's camera calibration (camera -> probe).
  eval   anchors only: one frame every --every usable rows, camera error against Polaris
         (--solver kabsch, or pnp without depth as rgbd-us scr.py).

  python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/v2-3XX
  python scr_anchor.py track --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/track-3XX
  python scr_anchor.py eval  --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX

Study options (results in summary.md 4; none adopted unless noted):
  --head small --label-max-depth 3000 --keep-depth-edges   the v1 recipe
  --aug-scale / --aug-rot          viewpoint augmentation (worse)
  --freeze-encoder                 head only on frozen ImageNet features (no gain)
  --render-views (scr_render.py)   rendered extra views from a voxel cloud or real frames (small gain)
  --confidence, track --weighted   confidence head + weighted Kabsch (no gain)
  --scan-seconds S                 only the first S seconds of each room scan (scan-length study)
  --max-frames                     smoke tests

Checkpoints keep scr.py's format (plus "head", "confidence"), so tools/anchoring_kabsch.py runs them in
the hybrid system. dataloader.py, geometry.py and scr.py are unchanged copies of rgbd-us modules.
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

from dataloader import RPRConfig, RPRDataset, load_hand_eye, test_sweeps   # noqa: E402
from scr import STRIDE, SCRNet, coord_targets, grid_pixels, load_depth_mm, localize   # noqa: E402


def bar(it, **kw):
    """Progress bar on stderr; in a log file it refreshes every 10 s so the log stays short."""
    return tqdm(it, mininterval=0.5 if sys.stderr.isatty() else 10, dynamic_ncols=True, leave=False, **kw)


# ---------------------------------------------------------------- network

class SCRNetFP32Head(SCRNet):
    """scr.SCRNet with the head outside autocast. Same parameters, so scr.load_scr loads it.
    Optional confidence head (`conf`, --confidence): forward_conf also returns the log of the expected
    coordinate error of each cell (metres); forward returns the coordinates only, as scr.SCRNet."""

    def __init__(self, pretrained=True):
        super().__init__(pretrained=pretrained)
        self.conf = None

    def forward(self, rgb):
        return self.forward_conf(rgb)[0]

    def forward_conf(self, rgb):
        f8 = self.low(rgb)
        f16 = F.interpolate(self.high(f8), size=f8.shape[-2:], mode="bilinear", align_corners=False)
        with torch.autocast(rgb.device.type, enabled=False):
            f = torch.cat([f8, f16], 1).float()
            # on detached features: the confidence learns from the coordinate error without changing the coordinates
            return self.head(f), (self.conf(f.detach()) if self.conf is not None else None)


class ConfHead(nn.Module):
    """Confidence head (--confidence): 1x1 convs 152 -> 128 -> 128 -> 1, the log expected coordinate error
    of each cell (m), clamped to 1 mm ... 1 m."""

    def __init__(self, cin=152, width=128):
        super().__init__()
        self.net = nn.Sequential(nn.Conv2d(cin, width, 1), nn.ReLU(inplace=True), nn.Conv2d(width, width, 1),
                                 nn.ReLU(inplace=True), nn.Conv2d(width, 1, 1))

    def forward(self, x):
        return self.net(x).clamp(math.log(1e-3), 0.0)


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


def build_net(head="small", pretrained=True, confidence=False):
    net = SCRNetFP32Head(pretrained=pretrained)
    if head == "big":
        net.head = BigHead()
    if confidence:
        net.conf = ConfHead()
    return net


def load_model(path, device):
    """scr.load_scr for either head: the checkpoint's "head" entry (absent = scr.py's small head)."""
    ck = torch.load(path, map_location=device, weights_only=False)
    net = build_net(ck.get("head", "small"), pretrained=False, confidence=ck.get("confidence", False)).to(device)
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
        none on depth edges, where a pixel's 3x3 neighbourhood spans more than 3 % of its depth;
      * camera_frame: targets in the camera frame (m, no pose, no centre) plus the item index, for
        training with learnable pose corrections (scr_map.py)."""

    def __init__(self, ds, root, items, centre, scale=(1.0, 1.0), rot=0.0, max_depth=None, drop_edges=False, seed=0,
                 camera_frame=False):
        self.ds, self.root, self.items, self.centre = ds, root, items, np.asarray(centre)
        self.log_scale, self.rot = np.log(scale), rot
        self.max_depth, self.drop_edges, self.seed = max_depth, drop_edges, seed
        self.camera_frame = camera_frame

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
        T = np.eye(4) if self.camera_frame else r["T_world_cam"][row]
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
        tgt = ((xyz[o::STRIDE, o::STRIDE] - (0.0 if self.camera_frame else self.centre)) / 1000.0).transpose(2, 0, 1)
        out = (torch.from_numpy(rgb.transpose(2, 0, 1).copy()).float(), torch.from_numpy(tgt.copy()).float(),
               torch.from_numpy(ok[o::STRIDE, o::STRIDE] > 0))
        return out + (i,) if self.camera_frame else out


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

def kabsch(P, Q, w=None):
    """R, t minimising |R P + t - Q| (weighted by w if given), P and Q (N, 3)."""
    if w is None:
        cp, cq = P.mean(0), Q.mean(0)
        U, _, Vt = np.linalg.svd((P - cp).T @ (Q - cq))
    else:
        w = w / w.sum()
        cp, cq = w @ P, w @ Q
        U, _, Vt = np.linalg.svd((P - cp).T @ ((Q - cq) * w[:, None]))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, cq - R @ cp


@torch.no_grad()
def cell_correspondences(net, ck, rgb, depth_mm, K, full_w, device, max_depth=2000.0, with_sigma=False):
    """(C, P), each (N, 3) mm: for every cell with measured depth below `max_depth`, its depth
    point in the camera frame (C) and its predicted room coordinate (P). Cells beyond max_depth are
    left out: depth noise grows with distance squared. with_sigma: also S (N,), the confidence head's
    expected error of each cell (mm), or None for a network without one."""
    x = torch.from_numpy(rgb).float()[None].to(device)
    pred, log_sigma = net.forward_conf(x) if hasattr(net, "forward_conf") else (net(x), None)
    pred = pred[0].double().cpu().numpy()
    h, w = pred.shape[1:]
    P = pred.reshape(3, -1).T * 1000.0 + np.asarray(ck["centre"])
    uv = grid_pixels(h, w, full_w / (w * STRIDE))
    ui = np.clip(np.round(uv[:, 0]).astype(int), 0, depth_mm.shape[1] - 1)
    vi = np.clip(np.round(uv[:, 1]).astype(int), 0, depth_mm.shape[0] - 1)
    z = depth_mm[vi, ui].astype(np.float64)
    m = (z > 100) & (z < max_depth)
    C = np.stack([(uv[:, 0] - K[0, 2]) / K[0, 0] * z, (uv[:, 1] - K[1, 2]) / K[1, 1] * z, z], 1)[m]
    if not with_sigma:
        return C, P[m]
    S = None if log_sigma is None else log_sigma[0, 0].exp().double().cpu().numpy().ravel()[m] * 1000.0
    return C, P[m], S


def localize_kabsch(net, ck, rgb, depth_mm, K, full_w, device, thr=20.0, max_depth=2000.0, min_inliers=30,
                    iters=256, rng=None, weighted=False):
    """Camera pose T_world_cam of one frame: Kabsch RANSAC (kabsch_ransac) on its cell correspondences;
    weighted (a checkpoint with a confidence head): cells weighted by their predicted error."""
    C, P, S = cell_correspondences(net, ck, rgb, depth_mm, K, full_w, device, max_depth, with_sigma=True)
    if weighted and S is None:
        raise SystemExit("--weighted needs a checkpoint trained with --confidence")
    return kabsch_ransac(C, P, thr, min_inliers, iters, rng, sigma=S if weighted else None)


def kabsch_ransac(C, P, thr=20.0, min_inliers=30, iters=256, rng=None, sigma=None):
    """T (4x4) mapping camera points C onto room points P, by RANSAC: hypotheses from 3 random
    correspondences (Kabsch), inliers within `thr` mm, refit three times on the inliers.
    sigma (N,), the expected error of each correspondence (mm): hypotheses sample cells with probability
    ~ 1 / sigma and the refits weight the inliers by 1 / sigma^2; inliers are still counted, so the gate
    keeps its meaning. Returns (T or None, number of inliers)."""
    if len(P) < max(min_inliers, 3):
        return None, 0
    rng = rng or np.random.default_rng(0)
    if sigma is None:
        idx = rng.integers(0, len(P), (iters, 3))
        w = None
    else:
        idx = rng.choice(len(P), (iters, 3), p=(1 / sigma) / (1 / sigma).sum())
        w = 1 / sigma ** 2
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
        R, t = kabsch(C[inl], P[inl], None if w is None else w[inl])
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
    if args.scan_seconds:                     # shorter room scans: the first S seconds of each run
        t0 = {n: min(ds.runs[n]["stamps"][r] for m, r in items if m == n) for n in args.scan_runs}
        items = [(n, r) for n, r in items if ds.runs[n]["stamps"][r] - t0[n] <= args.scan_seconds]
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
        from scr_render import RenderedViews, render_preview
        rendered = RenderedViews(ds, args.root, items, centre, args, device)
        render_preview(frames, rendered, out / "render_preview.jpg")
        data, n_rendered = ConcatDataset([frames, rendered]), len(rendered)
    # decoding two 1280 x 720 PNGs per sample, not the network, limits the speed
    dl = DataLoader(data, args.batch_size, shuffle=True, num_workers=args.workers, drop_last=True,
                    pin_memory=device.type == "cuda", persistent_workers=args.workers > 0,
                    prefetch_factor=4 if args.workers > 0 else None)
    net = build_net(args.head, confidence=args.confidence).to(device)
    encoder = list(net.low.parameters()) + list(net.high.parameters())
    if args.freeze_encoder:                   # ACE-style: ImageNet features as they are, only the head learns
        for q in encoder:
            q.requires_grad_(False)
    groups = [{"params": encoder, "lr": 0.0 if args.freeze_encoder else args.lr_encoder},
              {"params": net.head.parameters(), "lr": args.lr}]
    if args.confidence:
        groups.append({"params": net.conf.parameters(), "lr": args.lr})
    opt = torch.optim.AdamW(groups, weight_decay=1e-4)
    total = args.epochs * len(dl)
    sched = torch.optim.lr_scheduler.LambdaLR(opt, flatcos(total, max(1, total // 100), args.flat))
    amp = device.type == "cuda"
    scaler = torch.amp.GradScaler(enabled=amp)

    meta = {"args": vars(args), "centre": centre.tolist(), "image_size": list(args.image_size), "head": args.head,
            "confidence": args.confidence}
    json.dump(meta | {"n_frames": len(items), "n_rendered": n_rendered, "steps": total, "estimated_labels": label_err, "git": git_rev(REPO)},
              open(out / "config.json", "w"), indent=2)
    print(f"{len(dl)} steps per epoch, {total} in all; head {args.head} "
          f"({sum(p.numel() for p in net.head.parameters()) / 1e6:.2f} M); labels < {args.label_max_depth:g} mm"
          f"{', no depth edges' if args.drop_depth_edges else ''}; viewpoint augmentation "
          f"{f'zoom {args.aug_scale}, rotation +-{args.aug_rot} deg' if args.aug_rot or args.aug_scale != [1.0, 1.0] else 'off'}"
          f"{f'; + {n_rendered} rendered views' if n_rendered else ''}{'; encoder frozen' if args.freeze_encoder else ''}"
          f"{'; confidence head' if args.confidence else ''}",
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
                pred, log_sigma = net.forward_conf(rgb)
            err = torch.linalg.norm(pred.float() - tgt, dim=1)[ok]               # 3D distance, metres
            if err.numel() == 0:
                continue
            loss = coord_loss = err.mean()
            if log_sigma is not None:         # Laplace-type likelihood of the (detached) error: sigma learns the expected error
                s = log_sigma[:, 0][ok]
                loss = loss + (err.detach() / s.exp() + s).mean()
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            losses.append(coord_loss.item())            # the coordinate loss, comparable with models without confidence
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
            Tn, k = localize_kabsch(net, ck, rgb, depth, K, r["hw"][1], device, rng=np.random.default_rng(int(row)),
                                    weighted=args.weighted)
            inl[n] = k
            if Tn is not None and k >= args.gate:
                T[n] = Tn
        out[sw] = (rows, T, inl)
        print(f"  {sw}: {len(rows)} frames, {np.isfinite(T[:, 0, 0]).mean() * 100:.0f} % passed the gate", flush=True)
    return out


def smooth_poses(t, T, w, W, lag=None):
    """Robust local fit of the poses T (n, 4, 4; NaN = none) at times t, weights w, window W (s): quadratic in
    time inside the poses of the window, linear with fewer than 5, constant when extrapolating (gaps, ends).

    lag=None: the window is centred on each time (offline). lag=L (s): real time with a delay of L, the window
    is the last W s up to t + L, so only poses known by then are used; L = 0 is causal. The fit is then
    extrapolated to t (linear with at least 5 poses, else constant); no pose yet = NaN."""
    ok = np.isfinite(T[:, 0, 0])
    if ok.sum() < 3:
        return np.full_like(T, np.nan)
    tt, TT, ww = t[ok], T[ok], w[ok].astype(float)
    out = np.full_like(T, np.nan)
    for i in range(len(t)):
        if lag is None:
            m = np.abs(tt - t[i]) <= W / 2
            if m.sum() < 3:                                      # gap: widen to the 3 nearest poses
                m = np.zeros(len(tt), bool)
                m[np.argsort(np.abs(tt - t[i]))[:3]] = True
        else:
            known = tt <= t[i] + lag + 1e-9
            if not known.any():
                continue
            m = known & (tt >= t[i] + lag - W)
            if m.sum() < 3:                                      # gap: the 3 latest known poses
                m = np.zeros(len(tt), bool)
                m[np.flatnonzero(known)[-3:]] = True
        dt = tt[m] - t[i]
        k = (1 - np.clip(np.abs(dt) / max(W / 2 if lag is None else W, np.abs(dt).max() + 1e-6), 0, 1) ** 3) ** 3 * ww[m]
        inside = dt.min() < 0 < dt.max()                          # interpolating, not extrapolating
        if lag is None:
            order = 2 if (m.sum() >= 5 and inside) else 1 if (m.sum() >= 3 and inside) else 0
        else:
            order = 1 if m.sum() >= 5 else 0
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
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    cache = out / "poses.npz"
    meta = json.load(open(out / "poses.json")) if cache.exists() else {}
    cached = meta.get("every") == args.every and meta.get("weighted", False) == args.weighted
    if cached and Path(args.ckpt).exists() and Path(args.ckpt).stat().st_mtime > cache.stat().st_mtime:
        print(f"{args.ckpt} is newer than {cache}: tracking again")      # retrained into the same folder
        cached = False
    if cached:                                # smoothing only: no network needed (checkpoint may live elsewhere)
        hand_eye, image_size = REPO / "T_marker_cam.npy", (360, 640)
    else:
        net, ck = load_model(args.ckpt, device)
        hand_eye, image_size = resolve_hand_eye(ck["args"]["hand_eye"]), tuple(ck["image_size"])
    T_mc = load_hand_eye(hand_eye, "mm")
    ds = RPRDataset(args.test_root, test_sweeps(args.test_root, args.test_runs), [],
                    RPRConfig(T_marker_cam=T_mc, image_size=image_size))
    sweeps = list(ds.runs)
    if cached:
        z = np.load(cache)
        raw = {sw: (z[f"{sw}_rows"], z[f"{sw}_T"], z[f"{sw}_inl"]) for sw in sweeps}
        print(f"poses from {cache}")
    else:
        raw = track_poses(args, ds, sweeps, net, ck, device)
        np.savez_compressed(cache, **{f"{sw}_{k}": v for sw, (r, T, i) in raw.items() for k, v in (("rows", r), ("T", T), ("inl", i))})
        json.dump({"ckpt": args.ckpt, "every": args.every, "gate": args.gate, "weighted": args.weighted},
                  open(out / "poses.json", "w"))
    X = None
    if args.cam_calib:                        # map labels: camera pose x the probe's camera calibration (scr_map.py)
        X = np.asarray(json.load(open(args.cam_calib))["cam_calib"], float)
        raw = {sw: (r, T @ X, i) for sw, (r, T, i) in raw.items()}
        print(f"camera calibration from {args.cam_calib}: {np.linalg.norm(X[:3, 3]):.1f} mm, "
              f"{np.degrees(np.linalg.norm(Rotation.from_matrix(X[:3, :3]).as_rotvec())):.2f} deg")
    meta = json.load(open(out / "poses.json"))                  # raw poses stay uncalibrated; volume_pages.py reads this
    meta["cam_calib"] = None if X is None else X.tolist()
    json.dump(meta, open(out / "poses.json", "w"))

    scaling, rigid = read_us_calib(args.calib)
    P = np.linalg.inv(T_mc) @ rigid @ scaling @ np.stack([US_PX[:, 0], US_PX[:, 1], np.zeros(5), np.ones(5)])
    lags = [(f"real time {W:g} s, delay {L:g} s", W, L) for L in args.lags for W in args.windows]
    methods = ["raw"] + [f"smoothed {W:g} s" for W in args.windows] + [m for m, _, _ in lags]
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
        for m, W, L in lags:
            Ts = np.full_like(T, np.nan)
            for s in segs:
                Ts[s] = smooth_poses(t[s], T[s], inl[s], W, lag=L)
            ests[m] = Ts
        step8 = max(1, round(8 / args.every))
        for m, Te in ests.items():
            err, st = us_errors(Te, T_gt, P, segs, steps=(1, step8))
            res[m][sw] = {"us_median": float(np.nanmedian(err)), "us_p90": float(np.nanpercentile(err, 90)),
                          "coverage_pct": float(100 * np.isfinite(err).mean()), "step_row": st[1], "step_8rows": st[step8]}

    mean = lambda m, k: float(np.nanmean([v[k] for v in res[m].values()]))
    md = [f"# Single-model tracking: SCR alone on every {'' if args.every == 1 else f'{args.every}th '}row "
          f"({Path(args.test_root).name}, `{args.ckpt}`)", "",
          f"No odometry, no Polaris start pose; Kabsch RANSAC, gate >= {args.gate} inliers"
          f"{f'; camera calibration from `{args.cam_calib}`' if args.cam_calib else ''}. Error at the US image (5 points, "
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
    t.add_argument("--head", choices=["small", "big"], default="big",
                   help="big: ~2.2 M (final, v2); small: scr.py's 0.17 M head (v1)")
    t.add_argument("--label-max-depth", type=float, default=2000.0,
                   help="no training label beyond this depth (mm); 2000 final, 3000 in v1")
    t.add_argument("--drop-depth-edges", action="store_true", default=True,
                   help="no training label on depth edges (default; final recipe)")
    t.add_argument("--keep-depth-edges", dest="drop_depth_edges", action="store_false",
                   help="label depth edges too (v1)")
    t.add_argument("--freeze-encoder", action="store_true", help="train the head only on frozen ImageNet features (ACE-style)")
    t.add_argument("--render-views", type=float, default=0.0,
                   help="add this many rendered views per training frame (e.g. 0.5), new viewpoints from the room cloud")
    t.add_argument("--render-shift", type=float, default=150.0, help="rendered views: camera moved by up to this (mm)")
    t.add_argument("--render-rot", type=float, default=20.0, help="rendered views: camera turned by up to this (deg)")
    t.add_argument("--render-voxel", type=float, default=5.0, help="room cloud voxel size (mm)")
    t.add_argument("--render-every", type=int, default=4, help="room cloud from every n-th training frame")
    t.add_argument("--render-min-valid", type=float, default=0.5, help="keep a rendered view if this share of cells has a label")
    t.add_argument("--render-source", choices=["cloud", "frames"], default="cloud",
                   help="rendered views from the voxel room cloud, or from the nearest real frames at full resolution")
    t.add_argument("--render-frames", type=int, default=3, help="--render-source frames: real frames per rendered view")
    t.add_argument("--confidence", action="store_true",
                   help="also learn the expected error of each cell (for track --weighted)")
    t.add_argument("--scan-seconds", type=float, default=0.0,
                   help="room-scan length study: train on the first S seconds of each --scan-runs run only")
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
    k.add_argument("--lags", type=float, nargs="+", default=[],
                   help="also real-time smoothing with these delays (s; 0 = causal), for every window")
    k.add_argument("--weighted", action="store_true",
                   help="confidence checkpoints: sample and fit the Kabsch RANSAC with the predicted confidence")
    k.add_argument("--calib", default=str(REPO / "calib_matrix.csv"), help="US calibration (TUS-REC format)")
    k.add_argument("--cam-calib", default=None,
                   help="map.json of scr_map.py: for a network trained on map labels, apply its camera calibration "
                        "(fixed camera-frame transform) to every pose")
    k.add_argument("--out", required=True)
    args = ap.parse_args()
    {"train": train, "eval": evaluate, "track": track}[args.cmd](args)


if __name__ == "__main__":
    main()
