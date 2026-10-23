"""
Scene coordinate regression (SCR) for anchoring: a learned anchor with geometric outlier rejection.

The network (EfficientNet-B0 encoder, as RPRNet, with a per-pixel head instead of pose
regression) predicts for every cell of a stride-8 grid the 3D room coordinate (mm, Polaris
frame) of the surface seen there. The camera pose then follows from PnP + RANSAC on those
2D-3D pairs, so wrong predictions (moved objects, hands, glare) are outliers, as for the
classical anchors (note §6.5), and no keyframe retrieval or prior pose is needed.

Training is per room scan (the "scan the room, adapt for a few minutes" step; ACE / DSAC*
style): targets are the room-scan depth back-projected with the room-scan poses (Polaris
here, SLAM in a new room), so every pixel with depth is a label.

  # train on a block's room scans (about 10-20 min on the training PC)
  python scr.py train --root data/test_4XXA --scan-runs room-401 room-402 --out runs/scr-4XXA
  # anchor accuracy on the sweeps, every 1 s (camera position / rotation error vs Polaris)
  python scr.py eval --ckpt runs/scr-4XXA/best.pt --test-root data/test_4XXA
  # in the full system: anchoring.py evaluate ... --anchor scr --scr-ckpt runs/scr-4XXA/best.pt
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torchvision.models import EfficientNet_B0_Weights, efficientnet_b0

from dataloader import RPRConfig, RPRDataset, load_hand_eye, test_sweeps
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


class RoomScanFrames(Dataset):
    def __init__(self, ds, root, items, centre, aug, seed=0):
        self.ds, self.root, self.items, self.centre, self.aug = ds, root, items, centre, aug
        self.rng = np.random.default_rng(seed)
        H, W = ds.cfg.image_size
        self.h, self.w = H // STRIDE, W // STRIDE

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        name, row = self.items[i]
        r = self.ds.runs[name]
        bc = None
        if self.aug:                        # photometric only: no geometric augmentation
            bc = (self.rng.uniform(-0.2, 0.2), self.rng.uniform(0.8, 1.2), self.rng.uniform(0.9, 1.1, 3))
        rgb = self.ds.load_frame(name, row, bc)[0]
        d = load_depth_mm(self.ds, self.root, name, row)
        scale = r["hw"][1] / self.ds.cfg.image_size[1]
        tgt, ok = coord_targets(d, np.asarray(r["K"], float), r["T_world_cam"][row], self.h, self.w, scale,
                                self.ds.cfg.min_depth, self.ds.cfg.max_depth)
        tgt = ((tgt - self.centre) / 1000.0).transpose(2, 0, 1)
        return torch.from_numpy(rgb).float(), torch.from_numpy(tgt).float(), torch.from_numpy(ok)


def robust_loss(pred, tgt, ok, delta=0.05):
    """Huber on the 3D error (m) over the cells with depth; also the median error (mm)."""
    err = torch.linalg.norm(pred - tgt, dim=1)[ok]
    if err.numel() == 0:
        return pred.sum() * 0, float("nan")
    loss = torch.where(err < delta, 0.5 * err ** 2 / delta, err - 0.5 * delta).mean()
    return loss, float(err.median()) * 1000


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


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)
    T_mc = load_hand_eye(args.hand_eye, "mm")
    cfg = RPRConfig(T_marker_cam=T_mc, image_size=tuple(args.image_size))
    ds = RPRDataset(args.root, args.scan_runs, args.scan_runs, cfg)
    items = [(n, int(r)) for n in args.scan_runs for r in np.concatenate(ds.runs[n]["segments"])[:: args.frame_step]]
    centre = np.mean([ds.runs[n]["T_world_cam"][r][:3, 3] for n, r in items], 0)
    print(f"{len(items)} room-scan frames from {', '.join(args.scan_runs)} (every {args.frame_step}); "
          f"scene centre {np.round(centre).tolist()} mm")
    dl = DataLoader(RoomScanFrames(ds, args.root, items, centre, aug=True, seed=args.seed), args.batch_size,
                    shuffle=True, num_workers=args.workers, drop_last=True)
    net = SCRNet(pretrained=True).to(device)
    if args.init:
        net.load_state_dict(torch.load(args.init, map_location=device, weights_only=False)["model"])
    opt = torch.optim.AdamW([{"params": list(net.low.parameters()) + list(net.high.parameters()), "lr": args.lr_encoder},
                             {"params": net.head.parameters(), "lr": args.lr}], weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=[args.lr_encoder, args.lr], total_steps=args.epochs * len(dl))
    scaler = torch.amp.GradScaler(enabled=args.amp)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"args": vars(args), "centre": centre.tolist(), "image_size": list(args.image_size)}
    json.dump(meta, open(out / "config.json", "w"), indent=2)
    history = []
    for ep in range(args.epochs):
        net.train()
        losses, meds = [], []
        for rgb, tgt, ok in dl:
            rgb, tgt, ok = rgb.to(device), tgt.to(device), ok.to(device)
            with torch.autocast(device.type, enabled=args.amp):
                pred = net(rgb)
            loss, med = robust_loss(pred.float(), tgt, ok)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            losses.append(float(loss))
            meds.append(med)
        history.append({"epoch": ep + 1, "loss": float(np.mean(losses)), "coord_err_mm_median": float(np.nanmedian(meds))})
        print(f"epoch {ep + 1}/{args.epochs}: loss {history[-1]['loss']:.4f}, room-coordinate error median "
              f"{history[-1]['coord_err_mm_median']:.1f} mm (training frames)", flush=True)
        torch.save({"model": net.state_dict(), "epoch": ep, **meta}, out / "best.pt")
        json.dump(history, open(out / "history.json", "w"), indent=2)
    print(f"done -> {out / 'best.pt'}")


def evaluate(args):
    """Anchor accuracy on the sweeps of --test-root: one frame every --every rows, pose from
    SCR + PnP-RANSAC, camera position and rotation error against Polaris."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net, ck = load_scr(args.ckpt, device)
    T_mc = load_hand_eye(ck["args"]["hand_eye"], "mm")
    cfg = RPRConfig(T_marker_cam=T_mc, image_size=tuple(ck["image_size"]))
    sweeps = test_sweeps(args.test_root, args.test_runs)
    ds = RPRDataset(args.test_root, sweeps, [], cfg)
    rows, per = [], {}
    for sw in sweeps:
        r = ds.runs[sw]
        K = np.asarray(r["K"], float)
        for row in np.concatenate(r["segments"])[:: args.every]:
            T, n_inl = localize(net, ck, ds.load_frame(sw, int(row))[0], K, r["hw"][1], device, args.px, args.min_inliers)
            T_gt = r["T_world_cam"][row]
            if T is None:
                rows.append({"run": sw, "row": int(row), "solved": False, "inliers": n_inl})
                continue
            dR = T[:3, :3].T @ T_gt[:3, :3]
            rows.append({"run": sw, "row": int(row), "solved": True, "inliers": n_inl,
                         "err_mm": float(np.linalg.norm(T[:3, 3] - T_gt[:3, 3])),
                         "err_deg": float(np.degrees(np.arccos(np.clip((np.trace(dR) - 1) / 2, -1, 1))))})
        s = [x for x in rows if x["run"] == sw]
        ok = [x for x in s if x["solved"]]
        per[sw] = {"frames": len(s), "solved_pct": 100 * len(ok) / max(len(s), 1),
                   "err_mm_median": float(np.median([x["err_mm"] for x in ok])) if ok else None,
                   "err_mm_p90": float(np.percentile([x["err_mm"] for x in ok], 90)) if ok else None,
                   "err_deg_median": float(np.median([x["err_deg"] for x in ok])) if ok else None,
                   "inliers_median": float(np.median([x["inliers"] for x in s]))}
        p = per[sw]
        print(f"  {sw}: {p['frames']} frames, {p['solved_pct']:.0f} % solved, error median "
              f"{p['err_mm_median'] if p['err_mm_median'] is not None else float('nan'):.1f} mm (p90 "
              f"{p['err_mm_p90'] if p['err_mm_p90'] is not None else float('nan'):.1f}), "
              f"{p['err_deg_median'] if p['err_deg_median'] is not None else float('nan'):.2f} deg", flush=True)
    out = Path(args.out or Path(args.ckpt).parent / f"eval_{Path(args.test_root).name}")
    out.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(args), "per_sweep": per, "frames": rows}, open(out / "scr_eval.json", "w"), indent=1)
    f = lambda v, d=1: "–" if v is None else f"{v:.{d}f}"
    md = [f"# Scene coordinate anchors: {Path(args.ckpt).parent.name} on {Path(args.test_root).name}", "",
          f"One frame every {args.every} rows; pose from predicted room coordinates + PnP-RANSAC ({args.px:g} px, "
          f">= {args.min_inliers} inliers); camera position / rotation error against Polaris.", "",
          "| sweep | frames | solved | error mm (median / p90) | error deg | inliers |", "|---|---|---|---|---|---|"]
    md += [f"| {sw} | {p['frames']} | {p['solved_pct']:.0f} % | {f(p['err_mm_median'])} / {f(p['err_mm_p90'])} | "
           f"{f(p['err_deg_median'], 2)} | {p['inliers_median']:.0f} |" for sw, p in per.items()]
    ok = [x for x in rows if x["solved"]]
    md.append(f"| **all** | {len(rows)} | {100 * len(ok) / max(len(rows), 1):.0f} % | "
              f"{f(float(np.median([x['err_mm'] for x in ok])) if ok else None)} / "
              f"{f(float(np.percentile([x['err_mm'] for x in ok], 90)) if ok else None)} | "
              f"{f(float(np.median([x['err_deg'] for x in ok])) if ok else None, 2)} | |")
    (out / "scr_eval.md").write_text("\n".join(md) + "\n")
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'scr_eval.md'}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--root", required=True)
    t.add_argument("--scan-runs", nargs="+", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--hand-eye", default="T_marker_cam.npy")
    t.add_argument("--image-size", type=int, nargs=2, default=[360, 640])
    t.add_argument("--frame-step", type=int, default=2, help="use every n-th room-scan frame")
    t.add_argument("--epochs", type=int, default=15)
    t.add_argument("--batch-size", type=int, default=8)
    t.add_argument("--lr", type=float, default=1e-3, help="head")
    t.add_argument("--lr-encoder", type=float, default=1e-4)
    t.add_argument("--init", default=None, help="start from this SCR checkpoint")
    t.add_argument("--workers", type=int, default=8)
    t.add_argument("--amp", action="store_true")
    t.add_argument("--seed", type=int, default=0)
    e = sub.add_parser("eval")
    e.add_argument("--ckpt", required=True)
    e.add_argument("--test-root", required=True)
    e.add_argument("--test-runs", nargs="+", default=None)
    e.add_argument("--every", type=int, default=30, help="rows between evaluated frames (30 = 1 s)")
    e.add_argument("--px", type=float, default=10.0, help="RANSAC reprojection error (px, full resolution)")
    e.add_argument("--min-inliers", type=int, default=30)
    e.add_argument("--out", default=None)
    args = ap.parse_args()
    {"train": train, "eval": evaluate}[args.cmd](args)


if __name__ == "__main__":
    main()
