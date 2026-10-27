"""
Li et al. (TBME 2024) on OUR sweeps: the model reproduced on their forearm data (tools/li_repro.py,
runs/li-repro-M2) zero-shot, fine-tuned on our 2XX, or trained on our 2XX from scratch; scored with
the paper's metrics and against the camera system's relative motion.

Their network (EfficientNet-b1, two stacked frames of 120 x 160, 6 parameters) is rebuilt here
without their code; their weights load as a plain state dict (torch weights_only). It predicts the
motion T(tool1 -> tool0) of THEIR probe's tracking tool; the motion of the image plane is
T_img = R^-1 T_tool R with R their image-mm -> tool calibration (constants below, from
github.com/ucl-candi/freehand data/calib_matrix.csv), and our ground truth is the same image-plane
motion from Polaris through our calibration (inv(T_world_us_0) T_world_us_1, image mm). The image
grids match (both 640 x 480 before the 4x resampling; pixel size ours 0.230 x 0.221, theirs 0.224 x
0.236 mm: up to 6 % scale difference, not corrected).

Frames: new US frames (us_repeat = 0, ~19/s, theirs 20/s) of the usable rows (Polaris, probe on the
skin) of each segment; US crop resized to 640 x 480, then 4x down (their prep).

  finetune  pairs of consecutive new US frames of --root's sweeps except --val-runs; MSE on the 4
            image corners in image mm (their loss), Adam, batch 32; validation corner distance on
            --val-runs every --val-every steps, best kept. --init: their weights, or 'none' (scratch).
  eval      per segment, the scan is reconstructed by chaining the predicted frame-to-frame motion
            from its first frame (as their test.py): e_frame, e_acc (every 4th pixel of the 640 x 480
            image, all frames, vs frame 0), e_drift (last frame); zero motion alike. With --system
            (poses.py exports of the camera system), the relative motion between new US frames g
            apart (1, 5, 19 = ~1, 8, 30 rows) at the 5 US-image points of anchoring.py: in-plane and
            out-of-plane error of the US network, the system and zero motion (as tools/shape_error.py).

  python tools/li_transfer.py eval --weights runs/li-repro-M2/saved_model/best_validation_dist_model \\
      --root $DATA/train_3XX --system "runs/volume3d-final/3XX/poses/*anchored-pgo-scr-*.json" --out runs/li-transfer/zeroshot-3XX
  python tools/li_transfer.py finetune --init runs/li-repro-M2/saved_model/best_validation_dist_model \\
      --root $DATA/train_2XX --val-runs run-205 run-211 --out runs/li-transfer/ft-2XX
"""

import argparse
import glob
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import cv2                                                               # noqa: E402
import numpy as np                                                       # noqa: E402
import torch                                                             # noqa: E402
from tqdm import tqdm                                                    # noqa: E402

from dataloader import RPRConfig, RPRDataset, load_hand_eye, load_us_roi, test_sweeps   # noqa: E402
from shape_error import PX                                               # noqa: E402
from us_inplane import CALIB_HW, pd_num, read_calib                      # noqa: E402

THEIR_RIGID = np.array([[-0.22423702, 0.23241297, -0.94641533, -67.51702309],     # image mm -> tool
                        [-0.96461191, -0.19116474, 0.18160371, -79.75817299],
                        [-0.13871418, 0.95364577, 0.26705453, -49.03696251],
                        [0, 0, 0, 1]])
RESAMPLE = 4
GAPS = [1, 5, 19]


def build_net(M=2):
    """Their build_model(efficientnet_b1, in_frames=M, out_dim=6 * (M - 1)), rebuilt."""
    from torchvision.models import efficientnet_b1
    net = efficientnet_b1(weights=None)
    c = net.features[0][0]
    net.features[0][0] = torch.nn.Conv2d(M, c.out_channels, c.kernel_size, c.stride, c.padding, bias=False)
    net.classifier[1] = torch.nn.Linear(net.classifier[1].in_features, 6 * (M - 1))
    return net


def param_to_transform(p):
    """Their PredictionTransform.param_to_transform: (..., 6) -> (..., 4, 4) tool1 -> tool0."""
    cx, sx = torch.cos(p[..., 2]), torch.sin(p[..., 2])
    cy, sy = torch.cos(p[..., 1]), torch.sin(p[..., 1])
    cz, sz = torch.cos(p[..., 0]), torch.sin(p[..., 0])
    z, o = torch.zeros_like(cx), torch.ones_like(cx)
    rows = [torch.stack([cy * cz, sx * sy * cz - cx * sz, cx * sy * cz + sx * sz, p[..., 3]], -1),
            torch.stack([cy * sz, sx * sy * sz + cx * cz, cx * sy * sz - sx * cz, p[..., 4]], -1),
            torch.stack([-sy, sx * cy, cx * cy, p[..., 5]], -1),
            torch.stack([z, z, z, o], -1)]
    return torch.stack(rows, -2)


# Their code treats image rows as x (freehand/utils.py reference_image_points on frame_size = (h, w)); if
# their calibration does too, their image mm is (row, column, -normal) of ours. --axes picks the mapping
# (chosen on validation sweeps, as it cannot be read from the calibration file alone).
AXES = {"as-is": np.eye(4), "swap": np.array([[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]], float)}


class Motion:
    """Network output -> image-plane motion T_img(1 -> 0) in OUR image mm."""

    def __init__(self, device, axes="as-is"):
        F = torch.tensor(AXES[axes], dtype=torch.float32, device=device)                 # ours <- theirs (F = F^-1)
        R = torch.tensor(THEIR_RIGID, dtype=torch.float32, device=device)
        self.A, self.B = F @ torch.linalg.inv(R), R @ F

    def __call__(self, out):
        return self.A @ param_to_transform(out) @ self.B


def load_sweeps(root, runs, T_mc, rigid):
    """Per sweep and segment: new-US-frame rows, frames (n, 120, 160) uint8, T_world_us (n, 4, 4) image mm."""
    ds = RPRDataset(root, runs, [], RPRConfig(T_marker_cam=T_mc))
    out = {}
    for sw in runs:
        r = ds.runs[sw]
        df = r["df"]
        new = pd_num(df, "us_repeat") != 1
        has_us = df["us"].apply(lambda v: isinstance(v, str)).to_numpy()
        x0, y0, x1, y1 = load_us_roi(Path(root) / sw)
        T_world_us = r["T_world_cam"] @ np.linalg.inv(T_mc) @ rigid
        segs = []
        for seg in r["segments"]:
            rows = seg[new[seg] & has_us[seg]]
            if len(rows) < 3:
                continue
            fr = np.stack([cv2.resize(cv2.resize(cv2.imread(str(Path(root) / sw / df["us"].iloc[i]), cv2.IMREAD_GRAYSCALE)
                                                 [y0:y1, x0:x1], CALIB_HW[::-1], interpolation=cv2.INTER_LINEAR),
                                      None, fx=1 / RESAMPLE, fy=1 / RESAMPLE, interpolation=cv2.INTER_LINEAR)
                           for i in tqdm(rows, desc=f"{sw} frames", leave=False)])
            segs.append({"rows": rows, "frames": fr, "T": T_world_us[rows]})
        out[sw] = segs
        print(f"  {sw}: {len(segs)} segments, {sum(len(s['rows']) for s in segs)} new US frames", flush=True)
    return out


def corners_mm(scaling):
    w, h = CALIB_HW[1], CALIB_HW[0]
    px = np.array([[1, 1, 0, 1], [w, 1, 0, 1], [1, h, 0, 1], [w, h, 0, 1]], float).T   # 1-based calibration pixels
    return torch.tensor(scaling @ px, dtype=torch.float32)


def predict_steps(net, motion, frames, device, batch=64):
    """(n, 120, 160) uint8 -> (n - 1, 4, 4) predicted T_img(f + 1 -> f)."""
    x = torch.from_numpy(frames).float() / 255
    out = []
    with torch.no_grad():
        for a in range(0, len(x) - 1, batch):
            b = min(a + batch, len(x) - 1)
            pair = torch.stack([x[a:b], x[a + 1:b + 1]], 1).to(device)
            out.append(motion(net(pair)).cpu())
    return torch.cat(out).double()


def finetune(args):
    random.seed(args.seed)
    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    T_mc = load_hand_eye(args.hand_eye, "mm")
    scaling, rigid = read_calib(args.calib)
    sweeps = test_sweeps(args.root, args.runs)
    train_runs = [s for s in sweeps if s not in args.val_runs]
    print(f"train {train_runs}\nval {args.val_runs}")
    data = load_sweeps(args.root, train_runs + list(args.val_runs), T_mc, rigid)
    pairs = lambda runs: [(sw, k, i) for sw in runs for k, s in enumerate(data[sw]) for i in range(len(s["rows"]) - 1)]
    tr, va = pairs(train_runs), pairs(args.val_runs)[:: args.val_stride]
    if not tr or not va:
        raise SystemExit(f"no training ({len(tr)}) or validation ({len(va)}) pairs")

    def batch_of(items):
        x = torch.stack([torch.from_numpy(data[sw][k]["frames"][i:i + 2]) for sw, k, i in items]).float() / 255
        T = np.stack([np.linalg.inv(data[sw][k]["T"][i]) @ data[sw][k]["T"][i + 1] for sw, k, i in items])
        return x.to(device), torch.tensor(T, dtype=torch.float32, device=device)

    net = build_net().to(device)
    if args.init != "none":
        net.load_state_dict(torch.load(args.init, map_location=device, weights_only=True))
    motion, P = Motion(device, args.axes), corners_mm(scaling).to(device)
    opt = torch.optim.Adam(net.parameters(), lr=args.lr)
    out = Path(args.out)
    (out / "saved_model").mkdir(parents=True, exist_ok=True)
    json.dump({**vars(args), "train_pairs": len(tr), "val_pairs": len(va)}, open(out / "config.json", "w"), indent=1)

    def val_dist():
        net.train(False)
        d = []
        with torch.no_grad():
            for a in range(0, len(va), 64):
                x, T = batch_of(va[a:a + 64])
                d.append(torch.linalg.norm((motion(net(x)) @ P - T @ P)[:, :3], dim=1).mean(1).cpu())
        net.train(True)
        return float(torch.cat(d).mean())

    best = val_dist()
    torch.save(net.state_dict(), out / "saved_model" / "best_model")
    hist = [{"step": 0, "val_dist": best}]
    print(f"step 0 (init {args.init}): val corner distance {best:.3f} mm", flush=True)
    bar = tqdm(range(1, args.steps + 1), desc="finetune")
    run_loss = 0.0
    for step in bar:
        x, T = batch_of(random.sample(tr, args.batch_size))
        loss = torch.nn.functional.mse_loss(motion(net(x)) @ P, T @ P)
        opt.zero_grad()
        loss.backward()
        opt.step()
        run_loss += loss.item()
        if step % args.val_every == 0 or step == args.steps:
            d = val_dist()
            if d < best:
                best = d
                torch.save(net.state_dict(), out / "saved_model" / "best_model")
            hist.append({"step": step, "train_loss": run_loss / args.val_every, "val_dist": d})
            json.dump(hist, open(out / "history.json", "w"), indent=1)
            bar.set_postfix(loss=f"{run_loss / args.val_every:.3f}", val=f"{d:.3f}", best=f"{best:.3f}")
            run_loss = 0.0
    print(f"best val corner distance {best:.3f} mm -> {out / 'saved_model' / 'best_model'}")


def evaluate(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    T_mc = load_hand_eye(args.hand_eye, "mm")
    scaling, rigid = read_calib(args.calib)
    sweeps = test_sweeps(args.root, args.runs)
    system = {}
    for p in sorted(glob.glob(args.system)) if args.system else []:
        d = json.load(open(p))
        if d["run"] in sweeps and d["run"] not in system:
            system[d["run"]] = {f["row"]: np.asarray(f["T_world_us_pred"]) for f in d["frames"] if f["us"]}
    if args.system and not system:
        raise SystemExit(f"--system: no exports of {sweeps} match {args.system}")
    data = load_sweeps(args.root, sweeps, T_mc, rigid)
    net = build_net().to(device)
    net.load_state_dict(torch.load(args.weights, map_location=device, weights_only=True))
    net.train(False)
    motion = Motion(device, args.axes)

    w, h = CALIB_HW[1], CALIB_HW[0]
    vv, uu = np.mgrid[1:h + 1:4, 1:w + 1:4]
    P_all = torch.tensor(scaling @ np.stack([uu.ravel(), vv.ravel(), np.zeros(uu.size), np.ones(uu.size)]), dtype=torch.float64)
    P_c = corners_mm(scaling).double()
    P5 = torch.tensor(scaling @ np.stack([PX[:, 0], PX[:, 1], np.zeros(5), np.ones(5)]), dtype=torch.float64)
    dist = lambda A, B, P: torch.linalg.norm((A @ P - B @ P)[:, :3], dim=1)

    scans, rel = [], {}
    for sw in sweeps:
        for k, s in enumerate(data[sw]):
            steps = predict_steps(net, motion, s["frames"], device)
            T = [torch.eye(4, dtype=torch.float64)]
            for st in steps:
                T.append(T[-1] @ st)
            T = torch.stack(T)                                                     # frame f -> frame 0 (image mm)
            Tw = torch.from_numpy(s["T"])
            T_gt = torch.linalg.inv(Tw[0])[None] @ Tw
            Z = torch.eye(4, dtype=torch.float64).expand_as(T)
            m = lambda Tp: {"e_frame": dist(torch.linalg.inv(Tp[:-1]) @ Tp[1:], torch.linalg.inv(T_gt[:-1]) @ T_gt[1:], P_c).mean().item(),
                            "e_acc": dist(Tp[1:], T_gt[1:], P_all).mean().item(),
                            "e_drift": dist(Tp[-1:], T_gt[-1:], P_c).mean().item()}
            path = torch.linalg.norm(torch.diff((T_gt @ P5)[:, :3, 0], dim=0), dim=1).sum().item()
            scans.append({"run": sw, "segment": k, "frames": len(s["rows"]), "path_mm": path,
                          **m(T), **{f"zero_{a}": b for a, b in m(Z).items()}})
            sysT = system.get(sw)
            for g in GAPS:                                                         # relative motion, new US frames g apart
                i = np.arange(len(T) - g)
                if sysT is not None:
                    i = np.array([n for n in i if s["rows"][n] in sysT and s["rows"][n + g] in sysT], int)
                if not len(i):
                    continue
                rel_ = lambda Tf: torch.linalg.inv(Tf[i + g]) @ Tf[i]               # frame n in frame n + g
                E = {"US network": rel_(T), "zero motion": torch.eye(4, dtype=torch.float64).expand(len(i), 4, 4)}
                if sysT is not None:
                    Ts = torch.tensor(np.stack([sysT.get(r, np.eye(4)) for r in s["rows"]]))   # only pairs in the export are used
                    E["camera system"] = rel_(Ts)
                gt = rel_(T_gt)
                for name, Tp in E.items():
                    D = (Tp @ P5 - gt @ P5)[:, :3]
                    r = rel.setdefault((g, name), {"in": [], "out": [], "true": []})
                    r["in"] += torch.linalg.norm(D[:, :2], dim=1).mean(1).tolist()
                    r["out"] += D[:, 2].abs().mean(1).tolist()
                    r["true"] += (gt @ P5)[:, 2].abs().mean(1).tolist()

    ms = lambda key: (np.mean([x[key] for x in scans]), np.std([x[key] for x in scans]))
    md = [f"# Li et al. network on {Path(args.root).name}: `{args.weights}`, axes {args.axes}", "",
          f"{len(scans)} segments of {len(sweeps)} sweeps, new US frames only. Paper metrics, mean ± std over segments (mm); "
          "e_acc over every 4th pixel of the 640 × 480 image, all frames, relative to the segment's first frame.", "",
          "| | e_frame | e_acc | e_drift | drift / path |", "|---|---|---|---|---|"]
    drift_pct = lambda pre: 100 * np.mean([x[f"{pre}e_drift"] / max(x["path_mm"], 1e-6) for x in scans])
    md.append("| **US network** | " + " | ".join("%.2f ± %.2f" % ms(k) for k in ("e_frame", "e_acc", "e_drift"))
              + f" | {drift_pct(''):.1f} % |")
    md.append("| zero motion | " + " | ".join("%.2f ± %.2f" % ms(f"zero_{k}") for k in ("e_frame", "e_acc", "e_drift"))
              + f" | {drift_pct('zero_'):.1f} % |")
    if rel:
        md += ["", "Relative motion between new US frames g apart (~19 frames/s), error at the 5 US-image points of anchoring.py "
               "(mm, median / mean / p90 over pairs): in-plane, **out-of-plane**; true out-of-plane motion in brackets.", "",
               "| g | method | pairs | in-plane | **out-of-plane** |", "|---|---|---|---|---|"]
        for (g, name), r in sorted(rel.items(), key=lambda x: (x[0][0], x[0][1])):
            f3 = lambda v: f"{np.median(v):.2f} / {np.mean(v):.2f} / {np.percentile(v, 90):.2f}"
            md.append(f"| {g} ({np.median(r['true']):.1f} mm) | {name} | {len(r['in'])} | {f3(r['in'])} | **{f3(r['out'])}** |")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "li_transfer.md").write_text("\n".join(md) + "\n")
    json.dump({"args": vars(args), "scans": scans,
               "relative": {f"{g}|{n}": {k: float(np.median(v)) for k, v in r.items()} for (g, n), r in rel.items()}},
              open(out / "li_transfer.json", "w"), indent=1)
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'li_transfer.md'}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("finetune", "eval"):
        p = sub.add_parser(name)
        p.add_argument("--root", required=True, help="collection folder, e.g. $DATA/train_2XX")
        p.add_argument("--runs", nargs="+", default=None, help="sweeps (default: every run-* in --root)")
        p.add_argument("--out", required=True)
        p.add_argument("--hand-eye", default=str(REPO / "T_marker_cam.npy"))
        p.add_argument("--calib", default=str(REPO / "calib_matrix.csv"))
        p.add_argument("--axes", default="as-is", choices=list(AXES), help="their image axes -> ours (see AXES)")
        if name == "finetune":
            p.add_argument("--val-runs", nargs="+", required=True)
            p.add_argument("--init", required=True, help="their weights (e.g. runs/li-repro-M2/saved_model/best_validation_dist_model) or 'none'")
            p.add_argument("--steps", type=int, default=20000)
            p.add_argument("--val-every", type=int, default=500)
            p.add_argument("--val-stride", type=int, default=2, help="every n-th validation pair")
            p.add_argument("--batch-size", type=int, default=32)
            p.add_argument("--lr", type=float, default=1e-4)
            p.add_argument("--seed", type=int, default=0)
        else:
            p.add_argument("--weights", required=True)
            p.add_argument("--system", default=None, help="glob of poses.py exports of the camera system")
    args = ap.parse_args()
    finetune(args) if args.cmd == "finetune" else evaluate(args)


if __name__ == "__main__":
    main()
