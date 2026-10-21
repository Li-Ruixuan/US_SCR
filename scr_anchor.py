"""
SCR anchors, step S1 of the plan: rgbd-us `scr.py` (same network, targets, solver and test
protocol) with the optimisation fixed, plus the checks that tell whether it still underfits.

What S1 changes against scr.py, each a flag so the scr.py recipe can be rerun from this file:
  * every room-scan frame (--frame-step 1, scr.py: 2);
  * 3D distance loss (--loss dist; scr.py: Huber with a 50 mm knee, whose quadratic branch
    shrinks the gradient exactly where the error should go from cm to mm);
  * 4x the steps with a flat-then-cosine schedule (--sched flatcos; scr.py's OneCycle took the
    learning rate to zero while the error was still falling);
  * the head in fp32 (--fp32-head; under autocast the output is fp16, which is ~1-2 mm apart at
    1-2 m from the centre, i.e. the whole error budget).

Fit check (every --check-every epochs): a fixed set of training frames in eval mode, fp32,
no augmentation -- per-frame median coordinate error, the same after the best rigid fit
(what remains is noise RANSAC can average; the difference is a per-frame misalignment that
goes straight into the pose), and the PnP pose of the training frames themselves.

Evaluation = scr.py eval: one frame every 30 usable rows of the test sweeps (rgbd-us
RPRDataset: Polaris pose, not in the air, depth present), PnP-RANSAC 10 px, >= 30 inliers,
camera position / rotation error against Polaris. Added: a fixed RANSAC seed per frame,
p90 rotation, the mean of per-sweep medians next to the pooled median, and the time per frame.

Checkpoints keep scr.py's format, so `anchoring.py evaluate --anchor scr --scr-ckpt` takes them.

rgbd-us is imported from $RGBD_US (default: ../rgbd-us next to this repo).

  python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --out runs/s1-2XX \\
      --eval-root $DATA/train_2XX --eval-runs run-205 run-211
  python scr_anchor.py eval --ckpt runs/s1-2XX/best.pt --test-root $DATA/train_3XX
"""

import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

RGBD_US = Path(os.environ.get("RGBD_US", Path(__file__).resolve().parent.parent / "rgbd-us")).resolve()
sys.path.insert(0, str(RGBD_US))   # before this repo, whose old geometry.py would shadow rgbd-us's

import cv2                                                              # noqa: E402
import numpy as np                                                      # noqa: E402
import torch                                                            # noqa: E402
import torch.nn.functional as F                                         # noqa: E402
from torch.utils.data import DataLoader                                 # noqa: E402
from tqdm import tqdm                                                   # noqa: E402

from dataloader import RPRConfig, RPRDataset, load_hand_eye, test_sweeps   # noqa: E402
from scr import (STRIDE, RoomScanFrames, SCRNet, coord_targets, load_depth_mm,   # noqa: E402
                 load_scr, localize, robust_loss)


def bar(it, **kw):
    """Progress bar on stderr; in a log file (nohup) it refreshes every 10 s so the log stays short."""
    return tqdm(it, mininterval=0.5 if sys.stderr.isatty() else 10, dynamic_ncols=True, leave=False, **kw)


class SCRNetFP32Head(SCRNet):
    """scr.SCRNet with the head outside autocast. Same parameters, so scr.load_scr loads it."""

    def forward(self, rgb):
        f8 = self.low(rgb)
        f16 = F.interpolate(self.high(f8), size=f8.shape[-2:], mode="bilinear", align_corners=False)
        with torch.autocast(rgb.device.type, enabled=False):
            return self.head(torch.cat([f8, f16], 1).float())


def coord_loss(pred, tgt, ok, kind, delta):
    """(loss, median error mm) over the cells with depth; 'huber' is scr.robust_loss."""
    if kind == "huber":
        return robust_loss(pred, tgt, ok, delta)
    err = torch.linalg.norm(pred - tgt, dim=1)[ok]
    if err.numel() == 0:
        return pred.sum() * 0, float("nan")
    return err.mean(), float(err.detach().median()) * 1000


def flatcos(total, warmup, flat):
    """LR factor: linear warm-up, constant until `flat` of the steps, cosine to 0."""
    def f(s):
        if s < warmup:
            return (s + 1) / warmup
        if s < flat * total:
            return 1.0
        return 0.5 * (1 + math.cos(math.pi * (s - flat * total) / max(total - flat * total, 1)))
    return f


def kabsch(P, Q):
    """R, t minimising |R P + t - Q|, P and Q (N, 3)."""
    cp, cq = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - cp).T @ (Q - cq))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, cq - R @ cp


def pose_err(T, T_gt):
    dR = T[:3, :3].T @ T_gt[:3, :3]
    return (float(np.linalg.norm(T[:3, 3] - T_gt[:3, 3])),
            float(np.degrees(np.arccos(np.clip((np.trace(dR) - 1) / 2, -1, 1)))))


def git_rev(path):
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def resolve_hand_eye(path):
    """Absolute path; a relative one that does not exist here is taken from rgbd-us (old checkpoints)."""
    p = Path(path)
    if not p.is_absolute() and not p.exists():
        p = RGBD_US / p
    return str(p.resolve())


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


def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    torch.manual_seed(args.seed)
    args.hand_eye = resolve_hand_eye(args.hand_eye)
    cfg = RPRConfig(T_marker_cam=load_hand_eye(args.hand_eye, "mm"), image_size=tuple(args.image_size))
    ds = RPRDataset(args.root, args.scan_runs, args.scan_runs, cfg)
    items = [(n, int(r)) for n in args.scan_runs for r in np.concatenate(ds.runs[n]["segments"])[:: args.frame_step]]
    if args.max_frames:                     # smoke tests only
        items = items[:: max(1, len(items) // args.max_frames)][: args.max_frames]
    centre = np.mean([ds.runs[n]["T_world_cam"][r][:3, 3] for n, r in items], 0)
    check_items = [items[i] for i in np.linspace(0, len(items) - 1, min(args.check_frames, len(items))).astype(int)]
    print(f"{len(items)} room-scan frames from {', '.join(args.scan_runs)} (every {args.frame_step}); "
          f"scene centre {np.round(centre).tolist()} mm; fit check on {len(check_items)} of them", flush=True)

    # Decoding two 1280 x 720 PNGs per sample, not the network, limits the speed: keep the workers
    # between epochs, prefetch, and copy pinned batches asynchronously.
    dl = DataLoader(RoomScanFrames(ds, args.root, items, centre, aug=True, seed=args.seed), args.batch_size,
                    shuffle=True, num_workers=args.workers, drop_last=True, pin_memory=device.type == "cuda",
                    persistent_workers=args.workers > 0, prefetch_factor=4 if args.workers > 0 else None)
    net = (SCRNetFP32Head if args.fp32_head else SCRNet)(pretrained=True).to(device)
    opt = torch.optim.AdamW([{"params": list(net.low.parameters()) + list(net.high.parameters()), "lr": args.lr_encoder},
                             {"params": net.head.parameters(), "lr": args.lr}], weight_decay=1e-4)
    total = args.epochs * len(dl)
    if args.sched == "onecycle":
        sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=[args.lr_encoder, args.lr], total_steps=total)
    else:
        sched = torch.optim.lr_scheduler.LambdaLR(opt, flatcos(total, max(1, total // 100), args.flat))
    scaler = torch.amp.GradScaler(enabled=args.amp)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"args": vars(args), "centre": centre.tolist(), "image_size": list(args.image_size)}
    json.dump(meta | {"n_frames": len(items), "steps": total, "rgbd_us": str(RGBD_US),
                      "git": {"US_SCR": git_rev(Path(__file__).parent), "rgbd-us": git_rev(RGBD_US)}},
              open(out / "config.json", "w"), indent=2)
    print(f"{len(dl)} steps per epoch, {total} in all ({args.sched}, loss {args.loss}, "
          f"fp32 head {args.fp32_head})", flush=True)

    history = []
    for ep in range(args.epochs):
        net.train()
        t0, losses, meds = time.time(), [], []
        pbar = bar(dl, desc=f"epoch {ep + 1}/{args.epochs}")
        for rgb, tgt, ok in pbar:
            rgb, tgt, ok = (x.to(device, non_blocking=True) for x in (rgb, tgt, ok))
            with torch.autocast(device.type, enabled=args.amp):
                pred = net(rgb)
            loss, med = coord_loss(pred.float(), tgt, ok, args.loss, args.huber_delta)
            opt.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            sched.step()
            losses.append(loss.item())
            meds.append(med)
            pbar.set_postfix(loss=f"{losses[-1]:.4f}", err=f"{med:.0f} mm", refresh=False)
        h = {"epoch": ep + 1, "loss": float(np.mean(losses)), "coord_err_mm_median": float(np.nanmedian(meds)),
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
                                    every=30, px=args.px, min_inliers=args.min_inliers, seed=args.seed, out=None))


def evaluate(args):
    """scr.py eval with a fixed RANSAC seed per frame and both aggregations."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    net, ck = load_scr(args.ckpt, device)
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

    tag = Path(args.test_root).name + ("_" + "+".join(args.test_runs) if args.test_runs else "")
    out = Path(args.out or Path(args.ckpt).parent / f"eval_{tag}")
    out.mkdir(parents=True, exist_ok=True)
    json.dump({"args": vars(args), "all": allp, "per_sweep": per, "frames": rows}, open(out / "scr_eval.json", "w"),
              indent=1)
    f = lambda v, d=1: "–" if v is None else f"{v:.{d}f}"
    md = [f"# SCR anchors: {Path(args.ckpt).parent.name} on {tag}", "",
          f"One frame every {args.every} usable rows; PnP-RANSAC ({args.px:g} px, >= {args.min_inliers} inliers, "
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


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--root", required=True)
    t.add_argument("--scan-runs", nargs="+", required=True)
    t.add_argument("--out", required=True)
    t.add_argument("--hand-eye", default=str(RGBD_US / "T_marker_cam.npy"))
    t.add_argument("--image-size", type=int, nargs=2, default=[360, 640])
    t.add_argument("--frame-step", type=int, default=1, help="use every n-th room-scan frame (scr.py: 2)")
    t.add_argument("--epochs", type=int, default=30, help="scr.py: 15 at frame step 2, i.e. 1/4 of the steps")
    t.add_argument("--batch-size", type=int, default=8)
    t.add_argument("--lr", type=float, default=1e-3, help="head")
    t.add_argument("--lr-encoder", type=float, default=1e-4)
    t.add_argument("--sched", choices=["flatcos", "onecycle"], default="flatcos", help="scr.py: onecycle")
    t.add_argument("--flat", type=float, default=0.6, help="flatcos: share of the steps at full learning rate")
    t.add_argument("--loss", choices=["dist", "huber"], default="dist", help="scr.py: huber")
    t.add_argument("--huber-delta", type=float, default=0.05, help="m (scr.py: 0.05)")
    t.add_argument("--fp32-head", action=argparse.BooleanOptionalAction, default=True, help="scr.py: --no-fp32-head")
    t.add_argument("--amp", action=argparse.BooleanOptionalAction, default=True)
    t.add_argument("--workers", type=int, default=8)
    t.add_argument("--seed", type=int, default=0)
    t.add_argument("--check-every", type=int, default=3, help="epochs between fit checks")
    t.add_argument("--check-frames", type=int, default=120)
    t.add_argument("--max-frames", type=int, default=0, help="smoke tests only: cap the training frames")
    t.add_argument("--px", type=float, default=10.0)
    t.add_argument("--min-inliers", type=int, default=30)
    t.add_argument("--eval-root", default=None, help="evaluate on these sweeps after training")
    t.add_argument("--eval-runs", nargs="+", default=None)
    e = sub.add_parser("eval")
    e.add_argument("--ckpt", required=True)
    e.add_argument("--test-root", required=True)
    e.add_argument("--test-runs", nargs="+", default=None)
    e.add_argument("--every", type=int, default=30, help="usable rows between evaluated frames (30 = 1 s)")
    e.add_argument("--px", type=float, default=10.0, help="RANSAC reprojection error (px, full resolution)")
    e.add_argument("--min-inliers", type=int, default=30)
    e.add_argument("--seed", type=int, default=0)
    e.add_argument("--out", default=None)
    args = ap.parse_args()
    {"train": train, "eval": evaluate}[args.cmd](args)


if __name__ == "__main__":
    main()
