"""
Train the relative pose network on one leave-one-sweep-out fold, or on a fixed split. Basic version.

  python train.py --root data/train_2XX --scan-runs room-201 room-202 \
      --hand-eye T_marker_cam.npy --hand-eye-units mm --fold 0 --frame-gap 2
  # fixed split: named validation sweeps, every other run in --root trains (saved as fold0)
  python train.py --root data/train_2XX --scan-runs room-201 room-202 --val-runs run-205 run-210 ...

Before training: prints the zero-motion baseline on the val fold, per pair
AND per trajectory. A network near those numbers has learned nothing.

Every epoch: train loss + per-pair error, then val per-pair error and val
trajectory error, printed on the same line. best.pt = lowest val loss (or, with
--swa-epochs N, the weights averaged over the last N epochs):
aggregate drift% flatters zero motion on back-and-forth sweeps and jumps
between epochs with few segments, so it is reported but not used to select.
"""

import argparse
import dataclasses
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataloader import (RPRConfig, RPRDataset, chain_config, compute_target_stats,
                        load_hand_eye, split_runs)
from loss import RPRLoss, pair_errors
from model import RPRNet
from trajectory import (evaluate, gt_chains, model_inputs, predict, print_report,
                        zero_motion_preds)


def build(args):
    if args.hand_eye is None and not args.allow_no_hand_eye:
        raise SystemExit("--hand-eye is required: an identity T_marker_cam turns every rotation "
                         "into a wrong translation in the targets. "
                         "Use --allow-no-hand-eye for debugging only.")
    T_mc = load_hand_eye(args.hand_eye, args.hand_eye_units) if args.hand_eye else np.eye(4)
    if args.hand_eye is None:
        print("NO HAND-EYE: identity T_marker_cam -- debugging only, not reportable")

    train_runs, val_runs = split_runs(args.root, args.scan_runs, args.fold, args.val_runs)
    scans = [r for r in train_runs if r in args.scan_runs]
    sweeps = [r for r in train_runs if r not in args.scan_runs]
    if args.max_train_sweeps:            # data-size learning curve: a fixed random subset per fold
        rng = np.random.default_rng(1000 + args.fold)
        sweeps = sorted(rng.choice(sweeps, min(args.max_train_sweeps, len(sweeps)), replace=False).tolist())
    if args.rgb_from_us:                 # US-only arm: room scans have no US images
        if args.use_us or args.use_depth:
            raise SystemExit("--rgb-from-us is the US-only arm: do not combine with --use-us / --use-depth")
        scans = []
    if args.no_rgb:                      # US-only with the US motion branch: room scans have no US
        if not args.use_us or args.us_mode != "motion" or args.use_depth:
            raise SystemExit("--no-rgb is the US-only model: use it with --use-us --us-mode motion, without --use-depth")
        scans = []
    train_runs = scans + sweeps + (val_runs if args.include_val else [])
    print((f"fixed split" if args.val_runs else f"fold {args.fold}") + f": val={val_runs} | train={train_runs}"
          + ("  (UPPER BOUND: held-out sweep is also in training)" if args.include_val else ""))

    cfg = RPRConfig(T_marker_cam=T_mc, seq_len=args.seq_len, frame_gap=args.frame_gap,
                    window_step=args.window_step,
                    use_depth=args.use_depth, use_us=args.use_us, rgb_from_us=args.rgb_from_us,
                    use_rgb=not args.no_rgb,
                    image_size=tuple(args.image_size), us_size=tuple(args.us_size),
                    max_step_s=args.max_step_s,
                    spike_factor=args.spike_factor)
    print("train runs:")
    train_ds = RPRDataset(args.root, train_runs, args.scan_runs,
                          dataclasses.replace(cfg, augment=args.subset == 0,
                                              reverse_prob=args.reverse_prob))
    print("val runs:")
    val_ds = RPRDataset(args.root, val_runs, args.scan_runs, chain_config(cfg))

    mean, std = compute_target_stats(train_ds, args.robust_stats)   # train split only
    if args.subset:      # overfit check: fixed windows, no augmentation
        pick = np.random.default_rng(args.seed).choice(len(train_ds), args.subset, replace=False)
        train_ds.index = [train_ds.index[i] for i in pick]
    for ds in (train_ds, val_ds):
        ds.cfg.target_mean, ds.cfg.target_std = mean, std
    print(f"windows: train {len(train_ds)}, val {len(val_ds)}")
    return train_ds, val_ds, mean, std


def train_epoch(net, crit, loader, opt, scaler, device, mean, std, clip):
    net.train()
    total, n, t_err, r_err = 0.0, 0, [], []
    for batch in tqdm(loader, desc="train", leave=False):
        xi_gt = batch["xi"].to(device)
        with torch.autocast(device.type, enabled=scaler is not None):
            out = net(**model_inputs(batch, device))
            loss, _ = crit(out, {"xi": xi_gt})
        opt.zero_grad(set_to_none=True)
        if scaler is not None:
            scaler.scale(loss).backward()
            scaler.unscale_(opt)
            torch.nn.utils.clip_grad_norm_(net.parameters(), clip)
            scaler.step(opt)
            scaler.update()
        else:
            loss.backward()
            torch.nn.utils.clip_grad_norm_(net.parameters(), clip)
            opt.step()
        total += loss.item()
        n += 1
        t, r = pair_errors(out["xi"], batch["xi_raw"], mean, std)
        t_err.append(t)
        r_err.append(r)
    t, r = np.concatenate(t_err), np.concatenate(r_err)   # reduce once per epoch
    return {"loss": total / max(n, 1),
            "trans_mm_median": float(np.median(t)), "rot_deg_median": float(np.median(r))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/train")
    ap.add_argument("--scan-runs", nargs="+", required=True)
    ap.add_argument("--fold", type=int, default=0, help="leave-one-sweep-out fold (ignored with --val-runs)")
    ap.add_argument("--val-runs", nargs="+", default=None,
                    help="fixed split: these sweeps validate, every other run in --root trains")
    ap.add_argument("--out", default="runs/rpr")
    ap.add_argument("--hand-eye", default=None)
    ap.add_argument("--hand-eye-units", default="mm", choices=["mm", "m"])
    ap.add_argument("--allow-no-hand-eye", action="store_true",
                    help="debugging only: train with identity T_marker_cam")
    # data
    ap.add_argument("--seq-len", type=int, default=2)
    ap.add_argument("--frame-gap", type=int, default=1)
    ap.add_argument("--window-step", type=int, default=1,
                    help="rows between training window starts (longer --seq-len: e.g. 4, to keep epochs short)")
    ap.add_argument("--max-step-s", type=float, default=0.15)
    ap.add_argument("--spike-factor", type=float, default=5.0)
    ap.add_argument("--image-size", type=int, nargs=2, default=[360, 640])
    ap.add_argument("--us-size", type=int, nargs=2, default=[240, 320],
                    help="(H, W) of the US input; 240 320 is half the 640x480 calibration grid")
    ap.add_argument("--use-depth", action="store_true")
    ap.add_argument("--use-us", action="store_true")
    ap.add_argument("--us-mode", default="vector", choices=["vector", "motion"],
                    help="vector: old US branch (one pooled vector per frame); motion: US motion branch "
                         "(own trainable encoder, correlation + difference between frames)")
    ap.add_argument("--no-rgb", action="store_true",
                    help="US-only model (with --use-us --us-mode motion); room scans are left out")
    ap.add_argument("--rgb-from-us", action="store_true",
                    help="US-only arm: the US crop is the image input (same network); room scans are not used")
    ap.add_argument("--max-train-sweeps", type=int, default=0,
                    help="learning curve: train on N of the training sweeps (fixed per fold); 0 = all")
    ap.add_argument("--include-val", action="store_true",
                    help="upper bound only: also train on the held-out sweep (not a valid evaluation)")
    ap.add_argument("--use-dt", action="store_true")
    ap.add_argument("--temporal", default="none", choices=["none", "gru"],
                    help="context across the pairs of a window (needs --seq-len >= 3)")
    ap.add_argument("--swa-epochs", type=int, default=0,
                    help="average the weights of the last N epochs and save them as best.pt "
                         "(the single best epoch by val loss is kept as best_loss.pt)")
    ap.add_argument("--reverse-prob", type=float, default=0.0)
    ap.add_argument("--robust-stats", action="store_true")
    ap.add_argument("--val-every", type=int, default=1,
                    help="validate every N epochs (and always after the last)")
    ap.add_argument("--patience", type=int, default=0,
                    help="early stop after N validations without better drift; 0 = off")
    ap.add_argument("--subset", type=int, default=0,
                    help="overfit check: train on N fixed windows, augmentation off")
    # model / loss
    ap.add_argument("--no-pretrained", action="store_true")
    ap.add_argument("--corr-radius", type=int, default=3)
    ap.add_argument("--loss", default="huber", choices=["huber", "mmae"])
    ap.add_argument("--huber-delta", type=float, default=1.0)
    ap.add_argument("--w-rot", type=float, default=1.0)
    # optimisation
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--clip", type=float, default=5.0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--amp", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out = Path(args.out) / f"fold{args.fold}"
    out.mkdir(parents=True, exist_ok=True)
    print(f"device: {device}")

    train_ds, val_ds, mean, std = build(args)
    train_dl = DataLoader(train_ds, args.batch_size, shuffle=True, drop_last=True,
                          num_workers=args.workers, pin_memory=device.type == "cuda")
    val_dl = DataLoader(val_ds, args.batch_size, shuffle=False,   # order matters
                        num_workers=args.workers, pin_memory=device.type == "cuda")

    # -- baseline first ------------------------------------------------------
    chains = gt_chains(val_ds)
    base = evaluate(chains, zero_motion_preds(chains))
    print()
    print_report(base, "ZERO-MOTION BASELINE (val) -- must be beaten on BOTH lines")
    print()

    if args.temporal != "none" and args.seq_len < 3:
        raise SystemExit("--temporal needs --seq-len 3 or more (with 2 frames there is no context)")
    net = RPRNet(use_depth=args.use_depth, use_us=args.use_us,
                 pretrained=not args.no_pretrained, corr_radius=args.corr_radius,
                 use_dt=args.use_dt, temporal=args.temporal,
                 us_mode=args.us_mode, use_rgb=not args.no_rgb).to(device)
    crit = RPRLoss(delta=args.huber_delta, w_rot=args.w_rot, kind=args.loss)
    opt = torch.optim.AdamW(net.parameters(), lr=args.lr, weight_decay=args.weight_decay)
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=args.epochs)
    scaler = torch.amp.GradScaler() if (args.amp and device.type == "cuda") else None
    print(f"parameters: {sum(p.numel() for p in net.parameters()) / 1e6:.2f} M")

    json.dump(vars(args) | {"target_mean": mean.tolist(), "target_std": std.tolist(),
                            "baseline": base["pair"] | base["summary"]},
              open(out / "config.json", "w"), indent=2)

    best, history, stale = float("inf"), [], 0
    swa, n_swa = None, 0                     # running mean of the weights of the last --swa-epochs epochs
    for ep in range(args.epochs):
        t0 = time.time()
        tr = train_epoch(net, crit, train_dl, opt, scaler, device, mean, std, args.clip)
        sched.step()
        ckpt = {"model": net.state_dict(), "epoch": ep, "args": vars(args),
                "target_mean": mean, "target_std": std}
        torch.save(ckpt, out / "last.pt")
        if args.swa_epochs and ep >= args.epochs - args.swa_epochs:
            sd = {k: v.detach().float().clone() for k, v in net.state_dict().items()}
            if swa is None:
                swa = sd
            else:
                for k in swa:
                    swa[k] += (sd[k] - swa[k]) / (n_swa + 1)
            n_swa += 1
        if (ep + 1) % args.val_every and ep + 1 != args.epochs:
            print(f"[{ep + 1:3d}/{args.epochs}] train {tr['loss']:.4f} "
                  f"({tr['trans_mm_median']:.3f}mm {tr['rot_deg_median']:.3f}deg) | "
                  f"{time.time() - t0:.0f}s")
            history.append({"epoch": ep, "train": tr})
            json.dump(history, open(out / "history.json", "w"), indent=2)
            continue

        preds, val_loss = predict(net, val_dl, device, mean, std, crit)
        va = evaluate(chains, preds)
        p, s = va["pair"], va["summary"]
        print(f"[{ep + 1:3d}/{args.epochs}] "
              f"train {tr['loss']:.4f} ({tr['trans_mm_median']:.3f}mm {tr['rot_deg_median']:.3f}deg) | "
              f"val {val_loss:.4f} pair {p['trans_mm_median']:.3f}mm {p['rot_deg_median']:.3f}deg | "
              f"traj final {s['final_mm_median']:.2f}mm drift {s['drift_pct_aggregate']:.1f}% "
              f"(zero-motion {base['summary']['drift_pct_aggregate']:.1f}%) | {time.time() - t0:.0f}s")

        history.append({"epoch": ep, "train": tr, "val_loss": val_loss,
                        "val_pair": p, "val_traj": s})
        json.dump(history, open(out / "history.json", "w"), indent=2)

        if val_loss < best:
            best, stale = val_loss, 0
            torch.save(ckpt, out / "best.pt")
            json.dump(va | {"epoch": ep, "val_loss": val_loss},
                      open(out / "best_eval.json", "w"), indent=2)
            print(f"          new best: val loss {best:.4f}")
        else:
            stale += 1
            if args.patience and stale >= args.patience:
                print(f"          early stop: no better val loss in {stale} validations")
                break

    if swa is not None:                     # averaged weights replace the single best epoch
        (out / "best.pt").replace(out / "best_loss.pt")
        (out / "best_eval.json").replace(out / "best_loss_eval.json")
        ref = net.state_dict()
        net.load_state_dict({k: v.to(ref[k].dtype) for k, v in swa.items()})
        preds, val_loss = predict(net, val_dl, device, mean, std, crit)
        va = evaluate(chains, preds)
        torch.save({"model": net.state_dict(), "epoch": ep, "args": vars(args), "swa_epochs": n_swa,
                    "target_mean": mean, "target_std": std}, out / "best.pt")
        json.dump(va | {"epoch": ep, "val_loss": val_loss, "swa_epochs": n_swa},
                  open(out / "best_eval.json", "w"), indent=2)
        print(f"\nweights averaged over the last {n_swa} epochs: val {val_loss:.4f} "
              f"pair {va['pair']['trans_mm_median']:.3f}mm {va['pair']['rot_deg_median']:.3f}deg | "
              f"traj final {va['summary']['final_mm_median']:.2f}mm drift {va['summary']['drift_pct_aggregate']:.1f}% "
              f"-> best.pt (single best epoch by val loss: {best:.4f}, best_loss.pt)")
        best = val_loss
    print(f"\ndone. best val loss {best:.4f} -> {out / 'best.pt'}")
    print_report(json.load(open(out / "best_eval.json")), "best epoch, per segment:",
                 per_segment=True)


if __name__ == "__main__":
    main()
