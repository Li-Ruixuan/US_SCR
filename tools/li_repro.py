"""
Reproduction of Li et al., "Long-term dependency for 3D reconstruction of freehand ultrasound without
external tracker" (IEEE TBME 2024), with the authors' code and data, before using their network on ours.

Code: https://github.com/ucl-candi/freehand (cloned, --repo); data: Zenodo 7740734 (19 volunteers,
both forearms, 12 scans each = 228 scans, Ultrasonix 4DC7-3/40, 20 fps), converted to one .h5 by the
repo's data/prep.py (frames resampled 4x to 120 x 160). This script uses the repo's own modules
(loader, network, transforms, calibration) and only adds what its scripts lack: a fixed seed for the
random 3:1:1 scan-level split (5 folds: 0-2 train, 3 validation, 4 test, as scripts/train.py), a
progress bar, the number of epochs and the sequence length M as options, and the paper's metrics
(scripts/test.py only plots).

  train  as scripts/train.py: EfficientNet-b1 on M stacked frames, 'parameter' prediction, 'point'
         label (MSE on the 4 image corners in mm), Adam 1e-4, batch 32; M = 2 (the paper's baseline,
         adjacent frames) or M = 10 (the repo default: 10 frames within 10, the last 9 predicted
         against every earlier one). Validation every --val-every epochs; best_validation_dist_model
         is kept. The paper trains >= 20,000 epochs (one epoch = one random sequence per training scan).
  eval   test fold, every frame: the scan is reconstructed by chaining the prediction for the first
         pair (frame f -> f + 1) from frame 0, as scripts/test.py, and scored with the paper's metrics
         (Section III-E), mean +- std over test scans:
           e_frame  frame-to-frame: 4 corners, predicted vs true T(f+1 -> f), mm
           e_acc    accumulated tracking error: every image pixel of every frame, relative to frame 0, mm
           e_drift  final drift: 4 corners of the last frame, mm
         (e_dice, the volume overlap, is not computed.) Zero motion is scored the same way. The
         paper's Table I values for the same M are printed alongside.

  python tools/li_repro.py train --repo ~/freehand --h5 ~/freehand/data/Freehand_US_data/frames_res4.h5 --M 2 --out runs/li-repro-M2
  python tools/li_repro.py eval  --repo ~/freehand --out runs/li-repro-M2
"""

import argparse
import json
import os
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from tqdm import tqdm

PAPER = {2: {"e_frame": (0.53, 0.46), "e_acc": (22.75, 17.51), "e_drift": (29.59, 19.53)},     # Table I, CNN
         10: {"e_frame": (0.46, 0.56), "e_acc": (19.28, 13.25), "e_drift": (26.55, 13.29)}}


def repo_modules(repo):
    sys.path.insert(0, str(Path(repo).resolve()))
    from data.calib import read_calib_matrices
    from freehand.loader import SSFrameDataset
    from freehand.loss import PointDistance
    from freehand.network import build_model
    from freehand.transform import LabelTransform, PredictionTransform
    from freehand.utils import pair_samples, reference_image_points, type_dim
    return locals()


def setup(m, repo, M, frame_size, device):
    """Calibration, pairs, image points and transforms exactly as scripts/train.py."""
    calib = torch.tensor(m["read_calib_matrices"](filename_calib=str(Path(repo) / "data" / "calib_matrix.csv"),
                                                  resample_factor=4), device=device)
    pairs = m["pair_samples"](M, M - 1).to(device)
    pts = m["reference_image_points"](frame_size, 2).to(device)
    label = m["LabelTransform"]("point", pairs=pairs, image_points=pts, tform_image_to_tool=calib)
    pred = m["PredictionTransform"]("parameter", "point", num_pairs=pairs.shape[0], image_points=pts, tform_image_to_tool=calib)
    pred_tf = m["PredictionTransform"]("parameter", "transform", num_pairs=pairs.shape[0], image_points=pts,
                                       tform_image_to_tool=calib)
    out_dim = m["type_dim"]("parameter", pts.shape[1], pairs.shape[0])
    return calib, pairs, label, pred, pred_tf, out_dim


def train(args):
    m = repo_modules(args.repo)
    from torchvision.models import efficientnet_b1
    random.seed(args.seed)
    np.random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out = Path(args.out)
    (out / "saved_model").mkdir(parents=True, exist_ok=True)
    sample_range = args.sample_range or args.M

    ds = m["SSFrameDataset"](filename_h5=str(Path(args.h5).resolve()), num_samples=args.M, sample_range=sample_range)
    folds = ds.partition_by_ratio(ratios=[1] * 5, randomise=True, subject_level=False)
    for k, f in enumerate(folds):
        f.write_json(str(out / f"fold_{k:02d}.json"))
    d_train, d_val = folds[0] + folds[1] + folds[2], folds[3]
    tl = torch.utils.data.DataLoader(d_train, batch_size=args.batch_size, shuffle=True, num_workers=args.workers)
    vl = torch.utils.data.DataLoader(d_val, batch_size=1, shuffle=False, num_workers=1)

    _, _, label, pred, _, out_dim = setup(m, args.repo, args.M, d_train.frame_size, device)
    model = m["build_model"](efficientnet_b1, in_frames=args.M, out_dim=out_dim).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=args.lr)
    mse, dist_fn = torch.nn.MSELoss(), m["PointDistance"]()
    json.dump({**vars(args), "sample_range": sample_range, "train_scans": len(d_train), "val_scans": len(d_val),
               "test_scans": len(folds[4]), "frame_size": [int(x) for x in d_train.frame_size]},
              open(out / "config.json", "w"), indent=1)
    print(f"train {len(d_train)} / val {len(d_val)} / test {len(folds[4])} scans, M = {args.M}, "
          f"{args.epochs} epochs of {len(tl)} steps, {device}", flush=True)

    hist, best = [], float("inf")
    bar = tqdm(range(args.epochs), desc=f"M={args.M}")
    for ep in bar:
        model.train(True)
        tot = 0.0
        for frames, tf, tf_inv in tl:
            frames, tf, tf_inv = frames.to(device) / 255, tf.to(device), tf_inv.to(device)
            loss = mse(pred(model(frames)), label(tf, tf_inv))
            opt.zero_grad()
            loss.backward()
            opt.step()
            tot += loss.item()
        if ep % args.val_every == 0 or ep == args.epochs - 1:
            model.train(False)
            with torch.no_grad():
                d = np.mean([dist_fn(pred(model(f.to(device) / 255)), label(t.to(device), ti.to(device))).mean().item()
                             for f, t, ti in vl])
            if d < best:
                best = d
                torch.save(model.state_dict(), out / "saved_model" / "best_validation_dist_model")
            torch.save(model.state_dict(), out / "saved_model" / "last_model")
            hist.append({"epoch": ep, "train_loss": tot / len(tl), "val_dist": float(d), "time": time.time()})
            json.dump(hist, open(out / "history.json", "w"), indent=1)
            bar.set_postfix(loss=f"{tot / len(tl):.2f}", val_dist=f"{d:.2f}", best=f"{best:.2f}")
    print(f"best validation corner distance {best:.3f} mm -> {out / 'saved_model'}")


def tool_from_pixels(calib, h, w, step=1):
    """Homogeneous points in tool coordinates (mm) of the pixel grid (x = column, y = row), and of the 4 corners."""
    yy, xx = np.mgrid[0:h:step, 0:w:step]
    grid = np.stack([xx.ravel(), yy.ravel(), np.zeros(xx.size), np.ones(xx.size)]).astype(np.float32)
    corners = np.array([[0, 0, 0, 1], [w - 1, 0, 0, 1], [0, h - 1, 0, 1], [w - 1, h - 1, 0, 1]], np.float32).T
    return calib @ torch.from_numpy(grid), calib @ torch.from_numpy(corners)


def scan_metrics(T_pred, T_gt, P_all, P_c):
    """T_*: (N, 4, 4) tool_f -> tool_0. Paper metrics in mm."""
    d = lambda A, B, P: torch.linalg.norm((A @ P - B @ P)[:, :3], dim=1)      # (N, points)
    acc = d(T_pred[1:], T_gt[1:], P_all).mean().item()
    drift = d(T_pred[-1:], T_gt[-1:], P_c).mean().item()
    step = lambda T: torch.linalg.inv(T[:-1]) @ T[1:]                         # tool_{f+1} -> tool_f
    frame = d(step(T_pred), step(T_gt), P_c).mean().item()
    return {"e_frame": frame, "e_acc": acc, "e_drift": drift}


def evaluate(args):
    m = repo_modules(args.repo)
    from torchvision.models import efficientnet_b1
    out = Path(args.out)
    cfg = json.load(open(out / "config.json"))
    M = cfg["M"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    test = m["SSFrameDataset"].read_json(str(out / "fold_04.json"), num_samples=-1)
    calib, pairs, _, _, pred_tf, out_dim = setup(m, args.repo, M, test.frame_size, device)
    model = m["build_model"](efficientnet_b1, in_frames=M, out_dim=out_dim).to(device)
    model.load_state_dict(torch.load(out / "saved_model" / args.weights, map_location=device))
    model.train(False)
    h, w = (int(x) for x in test.frame_size)
    P_all, P_c = (p.cpu() for p in tool_from_pixels(calib.cpu(), h, w, args.pixel_step))

    rows = []
    for n in tqdm(range(len(test)), desc="test scans"):
        frames, tf, _ = test[n]
        frames = torch.tensor(frames, dtype=torch.float32, device=device) / 255
        tf = torch.tensor(tf, dtype=torch.float32)
        N = frames.shape[0]
        T_gt = torch.linalg.inv(tf[0])[None] @ tf                              # tool_f -> tool_0
        T = [torch.eye(4)]
        with torch.no_grad():
            for f0 in range(0, N - M + 1):                                      # pair 0 = (f0, f0 + 1), as test.py
                step = pred_tf(model(frames[f0:f0 + M][None]))[0, 0].cpu()
                T.append(T[-1] @ step)
        T += [T[-1]] * (N - len(T))                                             # last M - 2 frames: held (test.py)
        T = torch.stack(T)
        rows.append({"scan": list(test.indices_in_use[n]), "frames": N, **scan_metrics(T, T_gt, P_all, P_c),
                     **{f"zero_{k}": v for k, v in scan_metrics(torch.eye(4).expand(N, 4, 4), T_gt, P_all, P_c).items()}})

    ms = lambda k: (float(np.mean([r[k] for r in rows])), float(np.std([r[k] for r in rows])))
    paper = PAPER.get(M, {})
    md = [f"# Li et al. reproduction, M = {M} ({len(rows)} test scans, `{args.weights}`)", "",
          "Mean ± std over test scans (mm). e_acc over every pixel of every frame relative to frame 0, e_drift "
          "4 corners of the last frame, e_frame 4 corners frame to frame.", "",
          "| | e_frame | e_acc | e_drift |", "|---|---|---|---|",
          "| **this run** | " + " | ".join("%.2f ± %.2f" % ms(k) for k in ("e_frame", "e_acc", "e_drift")) + " |",
          "| zero motion | " + " | ".join("%.2f ± %.2f" % ms(f"zero_{k}") for k in ("e_frame", "e_acc", "e_drift")) + " |"]
    if paper:
        md.append("| paper, Table I (CNN) | " + " | ".join("%.2f ± %.2f" % paper[k] for k in ("e_frame", "e_acc", "e_drift")) + " |")
    (out / "li_repro_eval.md").write_text("\n".join(md) + "\n")
    json.dump({"args": vars(args), "M": M, "scans": rows}, open(out / "li_repro_eval.json", "w"), indent=1)
    print("\n".join(md[4:]) + f"\n-> {out / 'li_repro_eval.md'}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("train")
    t.add_argument("--repo", required=True, help="clone of github.com/ucl-candi/freehand")
    t.add_argument("--h5", required=True, help="frames_res4.h5 written by the repo's data/prep.py")
    t.add_argument("--M", type=int, default=2, help="sequence length: 2 = the paper's baseline, 10 = the repo default")
    t.add_argument("--sample-range", type=int, default=None, help="frames the M samples are drawn from (default M)")
    t.add_argument("--epochs", type=int, default=20000, help="the paper: at least 20,000")
    t.add_argument("--val-every", type=int, default=100)
    t.add_argument("--batch-size", type=int, default=32)
    t.add_argument("--lr", type=float, default=1e-4)
    t.add_argument("--workers", type=int, default=8)
    t.add_argument("--seed", type=int, default=0, help="split and initialisation")
    t.add_argument("--out", required=True)
    e = sub.add_parser("eval")
    e.add_argument("--repo", required=True)
    e.add_argument("--out", required=True, help="the train --out folder")
    e.add_argument("--weights", default="best_validation_dist_model", choices=["best_validation_dist_model", "last_model"])
    e.add_argument("--pixel-step", type=int, default=1, help="pixel grid step for e_acc (1 = every pixel)")
    args = ap.parse_args()
    os.environ.setdefault("CUDA_VISIBLE_DEVICES", "0")
    train(args) if args.cmd == "train" else evaluate(args)


if __name__ == "__main__":
    main()
