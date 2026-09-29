"""
Train the scene coordinate regressor.

  python3 train.py --root data --epochs 50 --hand-eye T_marker_cam.npy
  python3 train.py --root data --epochs 5 --calibration-pending   # debug only

What is different from the pairwise trainer
-------------------------------------------
* The loss is on coordinates, in millimetres. PoseLoss and its learned uncertainty
  scalars are gone -- they existed to reconcile metres with radians. 
* A predict-the-centroid baseline is printed before training starts. The head
  is zero-initialised, so an untrained network already emits the scene centroid
  and scores a finite, plausible-looking error. Without that number on screen
  there is no way to tell learning from the initialisation.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from dataset import SCRConfig, SCRDataset, build_splits, compute_scene_stats
from loss import CoordinateLoss, SequenceAuxLoss, coordinate_metrics
from model import SCRNet, pixel_grid
from solver import kabsch_ransac, pnp_ransac, pose_error


def load_hand_eye(path, units):
    """4x4 T_marker_cam from .npy, converted to millimetres and checked."""
    from geometry import POSE_UNITS
    T = np.load(path).astype(np.float64)
    if T.shape != (4, 4):
        raise ValueError(f"{path}: expected 4x4, got {T.shape}")
    T[:3, 3] *= POSE_UNITS[units]

    R = T[:3, :3]
    if not np.allclose(R.T @ R, np.eye(3), atol=1e-6):
        raise ValueError(f"{path}: rotation block is not orthonormal")
    if abs(np.linalg.det(R) - 1.0) > 1e-6:
        raise ValueError(f"{path}: det(R) != 1 (reflection or scale)")

    lever = np.linalg.norm(T[:3, 3])
    if not (1.0 <= lever <= 1000.0):
        raise ValueError(
            f"{path}: lever arm {lever:.1f} mm is implausible for a probe "
            f"mount. Check --hand-eye-units (you passed {units!r}).")
    print(f"hand-eye: lever arm {lever:.1f} mm from {path} ({units})")
    return T

def build_datasets(args):
    train_runs, val_runs = build_splits(
        args.root, args.val_runs, args.val_fraction, args.seed)
    print(f"train runs ({len(train_runs)}): {train_runs}")
    print(f"val   runs ({len(val_runs)}): {val_runs}")

    T_marker_cam = load_hand_eye(args.hand_eye, args.hand_eye_units) if args.hand_eye else None
    common = dict(pose_units=args.pose_units,
                  T_marker_cam=T_marker_cam,
                  calibration_pending=args.calibration_pending,
                  image_size=tuple(args.image_size),
                  max_depth=args.max_depth,
                  avg_frames=args.avg_frames,
                  seq_len=args.seq_len,
                  seq_stride=args.seq_stride)

    train_ds = SCRDataset(args.root, train_runs, SCRConfig(**common, augment=True))
    val_ds = SCRDataset(args.root, val_runs, SCRConfig(**common, augment=False))

    # Scene statistics from the training split only. Computing the room's
    # extent over validation frames would leak the validation viewpoints into
    # the normalisation the network is trained under.
    center, scale = compute_scene_stats(train_ds, args.stats_frames, args.seed)
    for ds in (train_ds, val_ds):
        ds.cfg.scene_center, ds.cfg.scene_scale = center, scale
    print(f"scene centre (mm): {np.round(center, 1)}   radius: {scale:.1f} mm")
    print(f"frames: train={len(train_ds)} val={len(val_ds)}")
    return train_ds, val_ds, center, scale


@torch.no_grad()
def centroid_baseline(ds, scale, n=64):
    """Error of predicting the scene centroid for every pixel.

    This is the number the model must beat to have learned anything at all.
    """
    errs = []
    for k in np.linspace(0, len(ds) - 1, min(n, len(ds))).astype(int):
        b = ds[int(k)]
        m = b["xyz_mask"] > 0
        d = b["xyz"].pow(2).sum(0, keepdim=True).sqrt()
        errs.append(d[m] * scale)
    return torch.cat(errs).median().item()


def plot_history(history, out_dir):
    """Train vs val loss over epochs, saved next to history.json."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    epochs = [h["epoch"] + 1 for h in history]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(epochs, [h["train"]["loss"] for h in history], label="train")
    ax.plot(epochs, [h["val"]["loss"] for h in history], label="val")
    ax.set_xlabel("epoch")
    ax.set_ylabel("loss")
    ax.set_title("train vs val loss")
    ax.legend()
    fig.tight_layout()
    path = Path(out_dir) / "loss_curve.png"
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"wrote {path}")


def move(batch, dev):
    return {k: (v.to(dev, non_blocking=True) if torch.is_tensor(v) else v)
            for k, v in batch.items()}


def train_epoch(net, crit, dl, dev, opt, scaler, clip=5.0,
                aux_crit=None, aux_weight=0.0, loss_scale=1.0):
    net.train()
    total, total_main, total_aux, n_batches, errs = 0.0, 0.0, 0.0, 0, []
    bar = tqdm(dl, desc="train", leave=False)
    for batch in bar:
        batch = move(batch, dev)
        with torch.autocast(dev.type, enabled=scaler is not None):
            out = net(batch["rgb"], batch["inv_depth"], batch["depth_mask"])
            main_loss, _ = crit(out, batch)
            if aux_crit is not None and aux_weight > 0.0:
                aux_loss = aux_crit(out, batch)
                loss = main_loss + aux_weight * aux_loss
            else:
                aux_loss = None
                loss = main_loss
            # Scale the complete objective, and each reported term the same
            # way, without changing the relative weighting between them.
            loss = loss_scale * loss
            main_loss = loss_scale * main_loss
            if aux_loss is not None:
                aux_loss = loss_scale * aux_loss

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
        total_main += main_loss.item()
        if aux_loss is not None:
            total_aux += aux_loss.item()
        n_batches += 1
        errs.append(coordinate_metrics(out, batch, net.scene_scale.item()).float().cpu())
        bar.set_postfix(loss=f"{total / n_batches:.4f}")

    out = {"loss": total / max(n_batches, 1),
           "main_loss": total_main / max(n_batches, 1),
           "coord_mm": torch.cat(errs).median().item()}
    if aux_crit is not None and aux_weight > 0.0:
        out["aux_loss"] = total_aux / max(n_batches, 1)
    return out


def bootstrap_group_ci(groups, values, n_boot=2000, ci=0.95, seed=0):
    """Bootstrap CI for the median of `values`, resampling whole `groups`.

    Consecutive validation frames are near-duplicates (median interframe
    translation 0.44mm, rotation 0.17deg in recorded data), so a thousand
    frames from two runs is closer to a few dozen independent viewpoints.
    Resampling individual frames would treat each near-duplicate as
    independent evidence and badly understate the interval; resampling whole
    groups (runs, or trajectory segments when too few runs exist) does not.

    Returns (lo, hi, n_groups).
    """
    groups = np.asarray(groups)
    values = np.asarray(values, dtype=np.float64)
    unique_groups = np.unique(groups)
    n = len(unique_groups)
    if n < 2 or len(values) == 0:
        return float("nan"), float("nan"), n

    by_group = {g: values[groups == g] for g in unique_groups}
    rng = np.random.default_rng(seed)
    boot = np.empty(n_boot)
    for k in range(n_boot):
        picked = rng.choice(unique_groups, size=n, replace=True)
        boot[k] = np.median(np.concatenate([by_group[g] for g in picked]))
    lo = float(np.percentile(boot, 100 * (1 - ci) / 2))
    hi = float(np.percentile(boot, 100 * (1 + ci) / 2))
    return lo, hi, n


def resample_labels(runs, frames, min_runs=5, seg_len=50):
    """Group label per validation frame for bootstrap_group_ci.

    Whole runs when there are enough of them to resample meaningfully;
    otherwise contiguous trajectory segments within each run, since
    resampling over individual frames is what this whole mechanism exists to
    avoid. seg_len=50 frames is short enough that a handful of segments fit
    even inside one modest validation run.
    """
    runs = np.asarray(runs)
    if len(np.unique(runs)) >= min_runs:
        return runs
    frames = np.asarray(frames)
    return np.array([f"{r}#{f // seg_len}" for r, f in zip(runs, frames)])


@torch.no_grad()
def validate(net, crit, dl, dev, args, aux_crit=None):
    """Coordinate metrics plus, optionally, solved pose metrics.

    aux_crit, if given, is reported (out["aux_loss"]) but never added into
    the returned "loss" -- validation loss is used for checkpoint selection
    and cross-run comparison, and folding in a term controlled by
    --aux-weight would make that comparison depend on a hyperparameter that
    has nothing to do with the main task.
    """
    net.eval()
    stride, off = net.stride, net.stride // 2
    total, total_aux, n_batches, errs = 0.0, 0.0, 0, []
    frame_runs, frame_idx, frame_coord_mm = [], [], []
    pose_runs, pose_frame_idx, t_err, r_err, solved, attempted = [], [], [], [], 0, 0

    bar = tqdm(dl, desc="val", leave=False)
    for bi, batch in enumerate(bar):
        batch = move(batch, dev)
        out = net(batch["rgb"], batch["inv_depth"], batch["depth_mask"])
        loss, _ = crit(out, batch)
        loss = args.loss_scale * loss
        total += loss.item()
        if aux_crit is not None:
            total_aux += (args.loss_scale * aux_crit(out, batch)).item()
        n_batches += 1
        errs.append(coordinate_metrics(out, batch, net.scene_scale.item()).float().cpu())
        bar.set_postfix(loss=f"{total / n_batches:.4f}")

        # E2: per-frame median, not just pooled per-pixel, so coord_mm can be
        # bootstrapped over runs below. Reuses coordinate_metrics per sample
        # rather than recomputing the distance formula here.
        B = out["xyz_norm"].shape[0]
        for b in range(B):
            pred_b = {"xyz_norm": out["xyz_norm"][b:b + 1]}
            batch_b = {"xyz": batch["xyz"][b:b + 1], "xyz_mask": batch["xyz_mask"][b:b + 1]}
            vals = coordinate_metrics(pred_b, batch_b, net.scene_scale.item())
            if vals.numel():
                frame_coord_mm.append(vals.median().item())
                frame_runs.append(batch["run"][b])
                frame_idx.append(int(batch["frame"][b]))

        if args.solve_every and bi % args.solve_every == 0:
            xyz = out["xyz"].float().cpu().numpy()          # (B, 3, h, w)
            B, _, h, w = xyz.shape
            uv = pixel_grid(h, w, net.stride).numpy()
            K = batch["K"].cpu().numpy()
            T_gt = batch["T_world_cam"].cpu().numpy().astype(np.float64)
            # D4 fix: xyz_mask requires the GT scene-coordinate label to be
            # valid, which is not something a deployed system can know --
            # it has no tracker. depth_mask only requires the measured depth
            # itself to be usable, which is available at real inference, so
            # that is what selects which cells reach the solver here. Cells
            # the network was never trained on (RealSense returned nothing)
            # now reach RANSAC as real outliers instead of being hidden by
            # the GT mask, which is what makes solve_rate below trustworthy.
            dmask_anchor = batch["depth_mask"][:, -1, 0].cpu().numpy()   # (B, H, W)
            mask = dmask_anchor[:, off::stride, off::stride].reshape(B, -1) > 0

            for b in range(B):
                pts = xyz[b].reshape(3, -1).T[mask[b]].astype(np.float64)
                pix = uv[mask[b]]
                attempted += 1
                T, inl = pnp_ransac(pts, pix, K[b].astype(np.float64),
                                    args.reproj_threshold)
                if T is None:
                    continue
                solved += 1
                dt, dr = pose_error(T, T_gt[b])
                t_err.append(dt)
                r_err.append(dr)
                pose_runs.append(batch["run"][b])
                pose_frame_idx.append(int(batch["frame"][b]))

    out = {"loss": total / max(n_batches, 1),
           "coord_mm": torch.cat(errs).median().item()}
    if aux_crit is not None:
        out["aux_loss"] = total_aux / max(n_batches, 1)

    coord_labels = resample_labels(frame_runs, frame_idx)
    lo, hi, n_groups = bootstrap_group_ci(coord_labels, frame_coord_mm, seed=args.seed)
    out["coord_mm_ci"] = (lo, hi)
    out["coord_mm_ci_groups"] = n_groups

    if attempted:
        # Since the D4 fix above, this is gated by depth_mask (real,
        # inference-time depth availability), not xyz_mask (GT validity) --
        # so unlike before, a rate below 100% is meaningful and this number
        # is no longer artificially optimistic.
        out["solve_rate"] = solved / attempted
        out["trans_mm"] = float(np.median(t_err)) if t_err else float("inf")
        out["rot_deg"] = float(np.median(r_err)) if r_err else float("inf")
        if t_err:
            pose_labels = resample_labels(pose_runs, pose_frame_idx)
            lo_p, hi_p, n_groups_p = bootstrap_group_ci(pose_labels, t_err, seed=args.seed)
            out["trans_mm_ci"] = (lo_p, hi_p)
            out["trans_mm_ci_groups"] = n_groups_p
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/train")
    ap.add_argument("--out", default="runs/scr1")
    ap.add_argument("--epochs", type=int, default=80)
    ap.add_argument("--sched-epochs", type=int, default=None,
                    help="length of the cosine LR schedule; defaults to  --epochs. E1: tying these together means the LR is "
                         "always a few percent of peak at the final epochs of any run, so validation flattening there is what a "
                         "finishing cosine schedule looks like regardless of whether the model has saturated. Set this longer "
                         "than --epochs to see a real knee instead.")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-4)
    ap.add_argument("--weight-decay", type=float, default=1e-4)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--amp", action="store_true", help="mixed precision on CUDA")
    ap.add_argument("--early-stop-patience", type=int, default=10,
                    help="stop training if the checkpoint-selection metric (trans_mm, or "
                         "coord_mm when the solver is disabled) hasn't improved for this many "
                         "consecutive epochs. 0 disables early stopping.")

    # data
    ap.add_argument("--pose-units", default="mm", choices=["mm", "m"],
                    help="units the tracker node publishes. The Polaris reports mm; check record_config.json per run.")
    ap.add_argument("--hand-eye", default=None, help=".npy 4x4 T_marker_cam. Required unless  --calibration-pending.")
    ap.add_argument("--calibration-pending", action="store_true", help="run with identity hand-eye for pipeline debugging.  Results are not valid and are flagged as such.")
    ap.add_argument("--val-runs", nargs="*", default=None,  help="name the held-out runs explicitly; prefer this over a random split for anything you intend to report")
    ap.add_argument("--val-fraction", type=float, default=0.2)
    ap.add_argument("--image-size", type=int, nargs=2, default=[360, 640],
                    help="(H, W), both divisible by 8. 360x640 is exactly  half of the 1280x720 sensor: full FoV, no crop.")
    ap.add_argument("--max-depth", type=float, default=3000.0,  help="millimetres")
    ap.add_argument("--avg-frames", type=int, default=1)
    ap.add_argument("--seq-len", type=int, default=2,
                    help="causal window length: the anchor frame plus (seq-len - 1) earlier frames, spaced --seq-stride "
                         "apart, as extra temporal context for the anchor's label. 1 (default) is the original single-frame "
                         "network -- not supported together with --avg-frames > 1.")
    ap.add_argument("--seq-stride", type=int, default=1, help="frame spacing within the --seq-len window")
    ap.add_argument("--stats-frames", type=int, default=200)
    ap.add_argument("--hand-eye-units", default=None, choices=["mm", "m"],
                    help="units of the translation block in the .npy. There is "
                         "no default: a wrong guess is a silent factor of 1000.")

    # model
    ap.add_argument("--backbone", default="efficientnet_b0")
    ap.add_argument("--head-width", type=int, default=256)
    ap.add_argument("--no-pretrained", action="store_true")
    ap.add_argument("--no-depth", action="store_true",
                    help="RGB-only ablation: this is standard SCR, and the "
                         "comparison against it is the depth contribution")
    ap.add_argument("--uncertainty", action="store_true", help="predict a per-cell log-variance channel")

    # loss / solver
    ap.add_argument("--huber-delta", type=float, default=0.05)
    ap.add_argument("--aux-weight", type=float, default=0.5,
                    help="weight on SequenceAuxLoss, the per-frame auxiliary loss over the whole --seq-len window (not just the "
                         "anchor frame). 0.0 (default) disables it entirely -- existing single-frame runs are unaffected. Only "
                         "meaningful with --seq-len > 1; at --seq-len 1 the auxiliary and main predictions are the same frame, "
                         "so it just doubles the gradient on a single view.")
    ap.add_argument("--loss-scale", type=float, default=100.0,
                    help="multiply the complete training objective by this value; does not change the relative balance between losses")
    ap.add_argument("--solve-every", type=int, default=4, help="run the pose solver on every Nth validation batch; 0 disables it")
    ap.add_argument("--reproj-threshold", type=float, default=3.0)
    args = ap.parse_args()

    if not args.hand_eye and not args.calibration_pending:
        ap.error("pass --hand-eye T_marker_cam.npy, or --calibration-pending "
                 "to debug the pipeline with identity extrinsics")
    if args.hand_eye and args.hand_eye_units is None:
        ap.error("--hand-eye requires --hand-eye-units {mm,m}")

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    dev = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    print(f"device: {dev}")

    train_ds, val_ds, center, scale = build_datasets(args)
    train_dl = DataLoader(train_ds, batch_size=args.batch_size, shuffle=True,
                          num_workers=args.workers, drop_last=True,
                          pin_memory=(dev.type == "cuda"))
    val_dl = DataLoader(val_ds, batch_size=args.batch_size, shuffle=False,
                        num_workers=args.workers,
                        pin_memory=(dev.type == "cuda"))

    base_mm = centroid_baseline(val_ds, scale)
    print(f"\nbaseline (predict scene centroid): {base_mm:.0f} mm")
    print("anything at or near this number means the network has not learned\n")

    net = SCRNet(backbone=args.backbone, pretrained=not args.no_pretrained,
                 use_depth=not args.no_depth, head_width=args.head_width,
                 predict_uncertainty=args.uncertainty,
                 seq_len=args.seq_len,
                 scene_center=torch.from_numpy(center).float(),
                 scene_scale=scale).to(dev)
    crit = CoordinateLoss(delta=args.huber_delta, uncertainty=args.uncertainty)
    aux_crit = SequenceAuxLoss(delta=args.huber_delta) if args.aux_weight > 0.0 else None
    print(f"parameters: {sum(p.numel() for p in net.parameters()) / 1e6:.2f} M")

    opt = torch.optim.AdamW(net.parameters(), lr=args.lr,
                            weight_decay=args.weight_decay)
    sched_epochs = args.sched_epochs or args.epochs
    sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=sched_epochs)
    scaler = torch.amp.GradScaler() if (args.amp and dev.type == "cuda") else None

    cfg = vars(args) | {"scene_center": center.tolist(), "scene_scale": scale,
                        "baseline_mm": base_mm,
                        "REPORTABLE": not args.calibration_pending}
    json.dump(cfg, open(out / "config.json", "w"), indent=2)

    best, history, epochs_since_improve = float("inf"), [], 0
    for ep in range(args.epochs):
        t0 = time.time()
        tr = train_epoch(net, crit, train_dl, dev, opt, scaler,
                         aux_crit=aux_crit, aux_weight=args.aux_weight,
                         loss_scale=args.loss_scale)
        va = validate(net, crit, val_dl, dev, args, aux_crit=aux_crit)
        sched.step()

        lo, hi = va["coord_mm_ci"]
        ci_str = (f" CI95[{lo:.1f},{hi:.1f}]/{va['coord_mm_ci_groups']}g"
                 if va["coord_mm_ci_groups"] >= 2 else " CI: too few groups")
        line = (f"[{ep + 1:3d}/{args.epochs}] "
                f"train {tr['loss']:.4f} ({tr['coord_mm']:6.1f}mm) | "
                f"val {va['loss']:.4f} ({va['coord_mm']:6.1f}mm{ci_str})")
        if "aux_loss" in tr:
            line += f" | aux train {tr['aux_loss']:.4f} val {va['aux_loss']:.4f}"
        if "trans_mm" in va:
            line += (f" | pose {va['trans_mm']:6.2f}mm {va['rot_deg']:.3f}deg"
                     f" ({100 * va['solve_rate']:.0f}% solved)")
        print(line + f" | {time.time() - t0:.0f}s")

        history.append({"epoch": ep, "train": tr, "val": va})
        json.dump(history, open(out / "history.json", "w"), indent=2)

        ckpt = {"model": net.state_dict(), "epoch": ep, "args": vars(args),
                "scene_center": center, "scene_scale": scale}
        torch.save(ckpt, out / "last.pt")

        # Select on solved pose error when available -- that is the quantity
        # the project is judged on -- and fall back to coordinate error only
        # when the solver is disabled.
        key = va.get("trans_mm", va["coord_mm"])
        if key < best:
            best = key
            epochs_since_improve = 0
            torch.save(ckpt, out / "best.pt")
            print(f"          new best {best:.2f}")
        else:
            epochs_since_improve += 1

        if args.early_stop_patience and epochs_since_improve >= args.early_stop_patience:
            print(f"\nno improvement in {epochs_since_improve} epochs -- "
                  f"stopping early after epoch {ep + 1}")
            break

    print(f"\ndone. best {best:.2f} -> {out / 'best.pt'}")
    if args.calibration_pending:
        print("CALIBRATION PENDING: these numbers are not reportable.")

    plot_history(history, out)


if __name__ == "__main__":
    main()
