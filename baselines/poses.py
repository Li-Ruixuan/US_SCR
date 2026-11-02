"""
Per-frame poses of the held-out sweeps: export, 3D plot, and US compounding.

  # everything for one arm: export (GPU, or the prediction cache), plots, compounding
  python poses.py --ckpts runs/rpr-rgb-gap4/fold*/best.pt
  # zero-motion baseline (CPU; identical for every arm)
  python poses.py --ckpts runs/rpr-rgb-gap4/fold*/best.pt --source zero --out runs/zero-motion-gap4
  # odometry + learned anchors (after anchoring.py evaluate; CPU)
  python poses.py --ckpts runs/rpr-rgb-gap4/fold*/best.pt --source anchored-offline-anchor-rgb-odometry
  # redo plots / compounding from exported JSON only (CPU, no checkpoints)
  python poses.py --json runs/rpr-rgb-gap4/poses/*_model.json --no-compound --us-every 20

1. Export. Poses are chained as in eval.py: each segment starts at the GT pose of its
   first frame, then composes predicted steps only (unanchored). The network predicts
   every frame_gap-th row ("keyframes"); rows in between are interpolated on SE(3) in
   time and flagged keyframe=false. Rows without tracking or US have no pose.
   <out>/poses/fold<k>_<run>_<source>.json: 4x4 T_world_cam and T_world_us (US image
   plane, mm), predicted and GT, file names, calibration. .csv: the same as position +
   quaternion (x, y, z, w). World = Polaris frame, mm. A calibration pixel (u, v),
   1-based on the 640x480 grid, maps to world as T_world_us @ S @ [u, v, 0, 1].
2. Plot. <stem>_3d.png and _3d.html: solid GT, dashed prediction, one colour per
   segment; --us-every N adds the US image outline every N keyframes.
3. Compound. Each US frame (ROI resized to the 640x480 calibration grid) is averaged into
   voxels (pixel nearest neighbour), once with GT and once with predicted poses, on a
   grid fitted to the GT volume. <out>/compound/<stem>/: metrics.json, slices.png,
   volumes.npz (unless --no-volume), and <out>/compound/summary_<source>.json over sweeps.
     pixel error   mean distance of each fan pixel, predicted vs GT pose (TUS-REC global
                   pixel error, from each segment's GT start)
     local error   the same for the step between consecutive keyframes (TUS-REC local)
     volume        NCC over voxels filled in either volume (ncc_union, empty = 0; the
                   headline) or in both (ncc_overlap, flatters collapsed volumes), and
                   Dice of the filled masks
<out> defaults to the arm folder (<arm>/poses, <arm>/compound).
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # dataloader.py, geometry.py at the repo root
from dataloader import load_us_roi
from eval import cached_preds, load_val_set, read_calib_parts
from geometry import invert_se3, se3_exp, se3_log
from trajectory import compose, gt_chains, zero_motion_preds


# --- export ---

def interpolate(key_rows, T_key, t_key, rows, t_rows):
    """SE(3) interpolation in time between consecutive keyframes.
    Returns (len(rows), 4, 4) for rows within [key_rows[0], key_rows[-1]]."""
    out = np.empty((len(rows), 4, 4))
    j = np.clip(np.searchsorted(key_rows, rows, side="right") - 1, 0, len(key_rows) - 2)
    xi = se3_log(invert_se3(T_key[:-1]) @ T_key[1:])                  # (K-1, 6)
    for n, (r, t) in enumerate(zip(rows, t_rows)):
        a = j[n]
        s = (t - t_key[a]) / max(t_key[a + 1] - t_key[a], 1e-9)
        out[n] = T_key[a] @ se3_exp(np.clip(s, 0, 1) * xi[a][None])[0]
    return out


def pose7(T):
    """(N, 4, 4) -> (N, 7) [x y z qx qy qz qw]."""
    return np.hstack([T[:, :3, 3], Rotation.from_matrix(T[:, :3, :3]).as_quat()])


def export_fold(path, args, device):
    """One checkpoint -> <stem>.json and <stem>.csv per held-out sweep; returns the JSON paths."""
    ck = torch.load(path, map_location=device, weights_only=False)
    ds, T_mc, val_runs = load_val_set(ck, args.test_root, args.test_runs)
    root = args.test_root or ck["args"]["root"]
    tag = Path(args.test_root).name if args.test_root else ""
    chains = gt_chains(ds)
    starts = {}                             # segment start poses; default: the true pose
    if args.source == "model":
        preds = cached_preds(path, ck, ds, device, args.batch_size, args.workers, tag)
    elif args.source == "zero":
        preds = zero_motion_preds(chains)
    else:                                   # e.g. anchored-offline-..., from anchoring.py evaluate
        f = Path(path).parent.parent / "preds" / f"{args.source}_fold{ck['args']['fold']}.npz"
        if not f.exists():
            raise SystemExit(f"{f} missing: run anchoring.py evaluate first")
        z = np.load(f, allow_pickle=True)
        preds = {(str(r), int(s)): v for (r, s), v in zip(z["keys"], z["values"])}
        if "starts" in z:                   # start poses not at the truth (anchoring.py --start anchor)
            starts = {(str(r), int(s)): v for (r, s), v in zip(z["keys"], z["starts"])}
    rigid, S = read_calib_parts()
    T_cam_us = invert_se3(T_mc) @ rigid                    # US image plane (mm) -> camera

    out_dir = (Path(args.out) if args.out else Path(path).parent.parent) / "poses"
    out_dir.mkdir(parents=True, exist_ok=True)
    fold = ck["args"]["fold"]
    outputs = []
    for run in val_runs:
        r = ds.runs[run]
        df, frames_out = r["df"], []
        for sid, seg in enumerate(r["segments"]):
            if (run, sid) not in chains or (run, sid) not in preds:
                continue                                    # shorter than one step
            c = chains[(run, sid)]
            key_rows = c["frames"]
            T_key = compose(starts.get((run, sid), c["T_gt"][0]), preds[(run, sid)])
            rows = seg[(seg >= key_rows[0]) & (seg <= key_rows[-1])]
            T_pred = interpolate(key_rows, T_key, c["t"], rows, r["stamps"][rows])
            T_gt = r["T_world_cam"][rows]
            is_key = np.isin(rows, key_rows)
            T_pred[is_key] = T_key[np.searchsorted(key_rows, rows[is_key])]
            for n, row in enumerate(rows):
                frames_out.append({
                    "row": int(row), "segment": sid, "t": float(r["stamps"][row]),
                    "keyframe": bool(is_key[n]),
                    "rgb": df["rgb"].iloc[row], "depth": df["depth"].iloc[row],
                    "us": df["us"].iloc[row] if isinstance(df["us"].iloc[row], str) else None,
                    "T_world_cam_pred": T_pred[n], "T_world_cam_gt": T_gt[n],
                    "T_world_us_pred": T_pred[n] @ T_cam_us, "T_world_us_gt": T_gt[n] @ T_cam_us})

        stem = out_dir / f"fold{fold}_{run}_{args.source}"
        meta = {"ckpt": str(path), "root": root, "fold": fold, "run": run, "source": args.source,
                "frame_gap": ck["args"]["frame_gap"], "units": "mm", "world": "Polaris",
                "chaining": "unanchored; each segment starts at its first GT pose",
                "T_marker_cam": T_mc.tolist(), "T_cam_us": T_cam_us.tolist(),
                "S_us_px_to_mm": S.tolist(),
                "us_roi": list(load_us_roi(Path(root) / run)),
                "us_pixels": "1-based on the US ROI resized to 640x480",
                "frames": [{k: (v.tolist() if isinstance(v, np.ndarray) else v)
                            for k, v in f.items()} for f in frames_out]}
        json.dump(meta, open(stem.with_suffix(".json"), "w"), indent=1)
        outputs.append(stem.with_suffix(".json"))

        cols = [f"{p}_{a}" for p in ("cam_pred", "cam_gt", "us_pred", "us_gt")
                for a in ("x", "y", "z", "qx", "qy", "qz", "qw")]
        mats = {p: np.stack([f[f"T_world_{p}"] for f in frames_out])
                for p in ("cam_pred", "cam_gt", "us_pred", "us_gt")}
        table = np.hstack([pose7(mats[p]) for p in ("cam_pred", "cam_gt", "us_pred", "us_gt")])
        with open(stem.with_suffix(".csv"), "w") as fh:
            fh.write("row,segment,t,keyframe,rgb,us," + ",".join(cols) + "\n")
            for f, v in zip(frames_out, table):
                fh.write(f"{f['row']},{f['segment']},{f['t']:.6f},{int(f['keyframe'])},"
                         f"{f['rgb']},{f['us'] or ''}," + ",".join(f"{x:.6f}" for x in v) + "\n")
        n_key = sum(f["keyframe"] for f in frames_out)
        print(f"  {run}: {len(frames_out)} frames ({n_key} keyframes) -> {stem}.json/.csv")
    return outputs


# --- 3D plot ---

COLOURS = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#9b59b6", "#e74c3c",
           "#16a085", "#7f8c8d", "#d35400", "#2c3e50"]


def load_segments(path):
    d = json.load(open(path))
    segs = {}
    for f in d["frames"]:
        segs.setdefault(f["segment"], []).append(f)
    return d, segs


def us_outline(T_world_us, S):
    """World corners (5, 3), closed, of the 640x480 calibration grid (1-based pixels)."""
    px = np.array([[1, 1, 0, 1], [640, 1, 0, 1], [640, 480, 0, 1], [1, 480, 0, 1], [1, 1, 0, 1]],
                  float).T
    return (T_world_us @ S @ px)[:3].T


def series(d, segs, what, us_every):
    """[(segment, colour, gt (N,3), pred (N,3), outlines [(gt (5,3), pred (5,3))])]"""
    S = np.asarray(d["S_us_px_to_mm"])
    out = []
    for n, (sid, fr) in enumerate(sorted(segs.items())):
        gt = np.array([np.asarray(f[f"T_world_{what}_gt"])[:3, 3] for f in fr])
        pr = np.array([np.asarray(f[f"T_world_{what}_pred"])[:3, 3] for f in fr])
        outl = []
        if us_every:
            keys = [f for f in fr if f["keyframe"]][::us_every]
            outl = [(us_outline(np.asarray(f["T_world_us_gt"]), S),
                     us_outline(np.asarray(f["T_world_us_pred"]), S)) for f in keys]
        out.append((sid, COLOURS[n % len(COLOURS)], gt, pr, outl))
    return out


def plot_html(d, ser, title, path):
    import plotly.graph_objects as go
    fig = go.Figure()
    for sid, col, gt, pr, outl in ser:
        fig.add_trace(go.Scatter3d(x=gt[:, 0], y=gt[:, 1], z=gt[:, 2], mode="lines",
                                   line=dict(color=col, width=5), name=f"seg {sid} GT",
                                   legendgroup=str(sid)))
        fig.add_trace(go.Scatter3d(x=pr[:, 0], y=pr[:, 1], z=pr[:, 2], mode="lines",
                                   line=dict(color=col, width=3, dash="dash"),
                                   name=f"seg {sid} pred", legendgroup=str(sid)))
        fig.add_trace(go.Scatter3d(x=gt[:1, 0], y=gt[:1, 1], z=gt[:1, 2], mode="markers",
                                   marker=dict(color=col, size=4), showlegend=False,
                                   legendgroup=str(sid)))
        for g, p in outl:
            for o, c, w in ((g, "#999999", 2), (p, col, 2)):
                fig.add_trace(go.Scatter3d(x=o[:, 0], y=o[:, 1], z=o[:, 2], mode="lines",
                                           line=dict(color=c, width=w), showlegend=False,
                                           legendgroup=str(sid)))
    fig.update_layout(title=title, scene=dict(aspectmode="data", xaxis_title="x (mm)",
                                              yaxis_title="y (mm)", zaxis_title="z (mm)"),
                      margin=dict(l=0, r=0, t=40, b=0))
    fig.write_html(path, include_plotlyjs="cdn")


def plot_png(ser, title, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(9, 8))
    ax = fig.add_subplot(projection="3d")
    for sid, col, gt, pr, outl in ser:
        ax.plot(*gt.T, "-", color=col, lw=1.5, label=f"seg {sid}")
        ax.plot(*pr.T, "--", color=col, lw=1.0)
        ax.scatter(*gt[0], color=col, s=15)
        for g, p in outl:
            ax.plot(*g.T, "-", color="#999999", lw=0.6)
            ax.plot(*p.T, "-", color=col, lw=0.6)
    pts = np.concatenate([np.vstack([gt, pr]) for _, _, gt, pr, _ in ser])
    ax.set_box_aspect(np.ptp(pts, 0) + 1e-6)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("z (mm)")
    ax.set_title(title + "\nsolid GT, dashed prediction", fontsize=10)
    if len(ser) <= 10:
        ax.legend(fontsize=7, loc="upper left")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)


def plot(path, args):
    d, segs = load_segments(path)
    ser = series(d, segs, args.what, args.us_every)
    title = f"fold {d['fold']}, {d['run']}, {d['source']} ({args.what}, unanchored)"
    stem = Path(path).with_suffix("")
    plot_png(ser, title, f"{stem}_3d.png")
    if not args.no_html:
        plot_html(d, ser, title, f"{stem}_3d.html")
    print(f"  wrote {stem}_3d.png" + ("" if args.no_html else " and .html"))


# --- US compounding ---

CALIB_HW = (480, 640)


def load_us(path, roi):
    x0, y0, x1, y1 = roi
    im = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    return cv2.resize(im[y0:y1, x0:x1], CALIB_HW[::-1], interpolation=cv2.INTER_AREA)


def fan_mask(frames, root, roi, thr, n=60):
    """Pixels that ever show signal over n evenly spaced frames: the US fan. Static screen
    overlays are masked, not cropped: pixels that stay bright but never change (depth-marker
    dots, the orientation dot, the probe-face line; std < 2 grey levels), grown by 2 px, and
    everything outside the largest connected region (small specks at the fan's edge)."""
    pick = frames[:: max(1, len(frames) // n)]
    stack = np.stack([load_us(root / f["us"], roi) for f in pick]).astype(np.float32)
    mx = stack.max(0)
    m = cv2.morphologyEx((mx > thr).astype(np.uint8), cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    static = ((stack.std(0) < 2.0) & (mx > 40)).astype(np.uint8)
    m[cv2.dilate(static, np.ones((5, 5), np.uint8)) > 0] = 0
    n_lab, lab, stats, _ = cv2.connectedComponentsWithStats(m)
    if n_lab > 1:
        m = (lab == 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))).astype(np.uint8)
    return m.astype(bool)


def pixel_points(mask, stride, S):
    """Fan pixels on a stride grid -> (rows, cols) and homogeneous image mm (4, P)."""
    r, c = np.nonzero(mask[::stride, ::stride])
    r, c = r * stride, c * stride
    px = np.stack([c + 1.0, r + 1.0, np.zeros(len(r)), np.ones(len(r))])   # 1-based (u, v)
    return r, c, S @ px


def accumulate(vol_sum, vol_cnt, origin, voxel, pts, vals):
    """Add world points (P, 3) with intensities into flat voxel sums; returns # dropped."""
    shape = vol_sum.shape
    ijk = np.floor((pts - origin) / voxel).astype(np.int64)
    ok = np.all((ijk >= 0) & (ijk < shape), axis=1)
    lin = np.ravel_multi_index(ijk[ok].T, shape)
    vol_sum.ravel()[:] += np.bincount(lin, vals[ok], vol_sum.size)
    vol_cnt.ravel()[:] += np.bincount(lin, minlength=vol_sum.size)
    return int((~ok).sum())


def ncc_over(a, b, m):
    """Normalised cross-correlation of two volumes over mask m (empty voxels count as 0)."""
    if not m.any():
        return float("nan")
    a, b = a[m] - a[m].mean(), b[m] - b[m].mean()
    return float((a * b).sum() / np.sqrt((a * a).sum() * (b * b).sum() + 1e-12))


def compound(d, args, out_dir):
    root = Path(d.get("root", args.root)) / d["run"]
    roi, S = d["us_roi"], np.asarray(d["S_us_px_to_mm"])
    frames = [f for f in d["frames"] if f["us"]]
    if args.keyframes_only:
        frames = [f for f in frames if f["keyframe"]]
    mask = fan_mask(frames, root, roi, args.fan_threshold)
    r, c, P_img = pixel_points(mask, args.stride, S)
    _, _, P_err = pixel_points(mask, args.err_stride, S)
    print(f"  {d['run']}: {len(frames)} frames, {P_img.shape[1]} fan pixels per frame "
          f"(stride {args.stride})")

    T_gt = np.array([f["T_world_us_gt"] for f in frames])
    T_pr = np.array([f["T_world_us_pred"] for f in frames])

    # pixel errors
    pix = np.linalg.norm((T_pr @ P_err - T_gt @ P_err)[:, :3], axis=1).mean(1)     # (F,)
    seg = np.array([f["segment"] for f in frames])
    key = [i for i, f in enumerate(frames) if f["keyframe"]]
    local = []
    for a, b in zip(key[:-1], key[1:]):
        if seg[a] != seg[b]:
            continue
        step_gt = np.linalg.inv(T_gt[a]) @ T_gt[b]
        step_pr = np.linalg.inv(T_pr[a]) @ T_pr[b]
        local.append(np.linalg.norm((T_gt[a] @ step_pr @ P_err - T_gt[a] @ step_gt @ P_err)[:3],
                                    axis=0).mean())
    final_per_seg = [float(pix[seg == s][-1]) for s in np.unique(seg)]

    # grid from the GT volume
    corners = S @ np.array([[1, 1, 0, 1], [640, 1, 0, 1], [640, 480, 0, 1], [1, 480, 0, 1]], float).T
    cw = (T_gt @ corners)[:, :3].transpose(0, 2, 1).reshape(-1, 3)
    origin = cw.min(0) - args.margin
    shape = tuple(np.ceil((cw.max(0) + args.margin - origin) / args.voxel).astype(int))
    n_vox = int(np.prod(shape))
    if n_vox * 16 > args.max_gb * 1e9:
        raise SystemExit(f"grid {shape} at {args.voxel} mm needs {n_vox * 16 / 1e9:.1f} GB; "
                         f"raise --voxel or --max-gb")
    vols = {}
    dropped = 0
    for name, T in (("gt", T_gt), ("pred", T_pr)):
        s, n = np.zeros(shape, np.float64), np.zeros(shape, np.float64)
        for i, f in enumerate(frames):
            vals = load_us(root / f["us"], roi)[r, c].astype(np.float64)
            pts = (T[i] @ P_img)[:3].T
            k = accumulate(s, n, origin, args.voxel, pts, vals)
            dropped += k if name == "pred" else 0
        vols[name] = (np.where(n > 0, s / np.maximum(n, 1), 0).astype(np.float32), n > 0)

    (vg, mg), (vp, mp) = vols["gt"], vols["pred"]
    both = mg & mp
    ncc, ncc_union = ncc_over(vg, vp, both), ncc_over(vg, vp, mg | mp)
    dice = float(2 * both.sum() / (mg.sum() + mp.sum()))
    n_pts = len(frames) * P_img.shape[1]
    metrics = {"run": d["run"], "fold": d["fold"], "source": d["source"],
               "frames": len(frames), "segments": int(len(np.unique(seg))),
               "pixel_error_mm": {"mean": float(pix.mean()), "median": float(np.median(pix)),
                                  "p95": float(np.percentile(pix, 95)),
                                  "final_per_segment": final_per_seg},
               "local_pixel_error_mm": {"mean": float(np.mean(local)) if local else None,
                                        "median": float(np.median(local)) if local else None,
                                        "n_steps": len(local)},
               "volume": {"voxel_mm": args.voxel, "shape": [int(x) for x in shape], "ncc_overlap": ncc, "ncc_union": ncc_union,
                          "dice": dice,
                          "pred_pixels_outside_grid_pct": 100 * dropped / n_pts}}
    out_dir.mkdir(parents=True, exist_ok=True)
    json.dump(metrics, open(out_dir / "metrics.json", "w"), indent=2)
    if not args.no_volume:
        np.savez_compressed(out_dir / "volumes.npz", gt=vg, pred=vp, mask_gt=mg, mask_pred=mp,
                            origin=origin, voxel=args.voxel)
    plot_slices(vg, vp, pix, frames, metrics, out_dir / "slices.png")
    print(f"    pixel error mean {pix.mean():.1f} mm (median {np.median(pix):.1f}), local "
          f"{metrics['local_pixel_error_mm']['median'] or float('nan'):.2f} mm | volume NCC {ncc_union:.3f} "
          f"(overlap only {ncc:.3f}), Dice {dice:.3f}, {metrics['volume']['pred_pixels_outside_grid_pct']:.1f}% pred pixels "
          f"outside grid -> {out_dir}")
    return metrics


def plot_slices(vg, vp, pix, frames, m, path):
    """Maximum intensity projections along each world axis, GT vs prediction, and the
    pixel error over time."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 3, figsize=(13, 11), gridspec_kw={"height_ratios": [1, 1, 0.6]})
    for j, (axis, lab) in enumerate([(2, "z"), (1, "y"), (0, "x")]):
        for i, (v, name) in enumerate([(vg, "GT poses"), (vp, "predicted poses")]):
            ax[i, j].imshow(v.max(axis).T, cmap="gray", origin="lower", vmin=0, vmax=255)
            ax[i, j].set_title(f"{name}: MIP along world {lab}", fontsize=9)
            ax[i, j].axis("off")
    gs = ax[2, 0].get_gridspec()
    for a in ax[2]:
        a.remove()
    a = fig.add_subplot(gs[2, :])
    t = np.array([f["t"] for f in frames])
    seg = np.array([f["segment"] for f in frames])
    for s in np.unique(seg):
        k = seg == s
        a.plot(t[k] - t[0], pix[k], "-", lw=1, label=f"seg {s}")
    a.set_xlabel("time in sweep (s)")
    a.set_ylabel("pixel error (mm)")
    a.set_title("mean distance of US pixels, predicted vs GT pose (each segment starts at GT)",
                fontsize=9)
    a.legend(fontsize=7, ncol=6)
    fig.suptitle(f"fold {m['fold']}, {m['run']}, {m['source']}: NCC {m['volume']['ncc_union']:.3f}, Dice {m['volume']['dice']:.2f}, "
                 f"pixel error {m['pixel_error_mm']['mean']:.1f} mm", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--ckpts", nargs="+", help="export from these checkpoints, then plot/compound")
    src.add_argument("--json", nargs="+", help="plot/compound already exported JSON only")
    ap.add_argument("--source", default="model",
                    help="model: the network (GPU or cache); zero: zero-motion baseline (CPU); "
                         "anything else: <arm>/preds/<source>_fold<k>.npz, e.g. the "
                         "anchored-offline-... trajectories written by anchoring.py evaluate")
    ap.add_argument("--out", default=None, help="default: the arm folder (give one per test set)")
    ap.add_argument("--test-root", default=None,
                    help="export the sweeps of this folder instead of the validation sweeps")
    ap.add_argument("--test-runs", nargs="+", default=None, help="with --test-root: only these (default: every run-*)")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--workers", type=int, default=8)
    g = ap.add_argument_group("plot")
    g.add_argument("--no-plot", action="store_true")
    g.add_argument("--what", default="cam", choices=["cam", "us"],
                   help="trajectory of the camera centre or of the US image origin")
    g.add_argument("--us-every", type=int, default=0,
                   help="draw the US image outline every N keyframes (0 = off)")
    g.add_argument("--no-html", action="store_true")
    g = ap.add_argument_group("compound")
    g.add_argument("--no-compound", action="store_true")
    g.add_argument("--root", default="data/train", help="if the JSON has no root")
    g.add_argument("--voxel", type=float, default=1.0, help="mm")
    g.add_argument("--stride", type=int, default=2, help="pixel stride for compounding")
    g.add_argument("--err-stride", type=int, default=8, help="pixel stride for the errors")
    g.add_argument("--margin", type=float, default=5.0, help="mm around the GT volume")
    g.add_argument("--fan-threshold", type=float, default=5.0)
    g.add_argument("--keyframes-only", action="store_true",
                   help="only frames the network predicted (no interpolated poses)")
    g.add_argument("--max-gb", type=float, default=8.0)
    g.add_argument("--no-volume", action="store_true", help="skip writing volumes.npz")
    args = ap.parse_args()

    if args.ckpts:
        device = torch.device("cuda" if torch.cuda.is_available() and args.source == "model"
                              else "cpu")
        jsons = []
        for p in args.ckpts:
            print(f"\n=== {p}")
            jsons += export_fold(p, args, device)
    else:
        jsons = [Path(p) for p in args.json]

    if not args.no_plot:
        print("\n=== 3D plots")
        for p in jsons:
            plot(p, args)

    if not args.no_compound:
        print("\n=== US compounding")
        allm = []
        for p in jsons:
            d = json.load(open(p))
            allm.append(compound(d, args, Path(p).parent.parent / "compound" / Path(p).stem))
        if allm:
            keys = {"pixel_error_mm": lambda m: m["pixel_error_mm"]["mean"],
                    "local_pixel_error_mm": lambda m: m["local_pixel_error_mm"]["median"],
                    "ncc_union": lambda m: m["volume"]["ncc_union"],
                    "dice": lambda m: m["volume"]["dice"]}
            summ = {"per_sweep": {m["run"]: {k: f(m) for k, f in keys.items()} for m in allm},
                    "mean": {k: float(np.nanmean([f(m) for m in allm])) for k, f in keys.items()}}
            src = json.load(open(jsons[0]))["source"]
            out = Path(jsons[0]).parent.parent / "compound" / f"summary_{src}.json"
            json.dump(summ, open(out, "w"), indent=2)
            s = summ["mean"]
            print(f"\n  mean over {len(allm)} sweeps: pixel error {s['pixel_error_mm']:.1f} mm, "
                  f"local {s['local_pixel_error_mm']:.2f} mm, NCC {s['ncc_union']:.3f}, "
                  f"Dice {s['dice']:.3f} -> {out}")


if __name__ == "__main__":
    main()
