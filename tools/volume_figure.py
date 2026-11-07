"""
Static figure of a compounded US sweep for the paper: the same US images placed with the true poses (Polaris)
and with each estimate, on one common grid, shown as three orthogonal slab projections (maximum intensity in a
slab around the volume centre), plus an overlay per estimate (true in green, estimate in magenta, white where
they agree). --rigid-fit adds each estimate after the best rigid fit of the whole sweep to Polaris: what is
left is the volume's distortion (the "shape" of tools/us_analysis.py), the rest was placement.

The grid follows the probe: its axes are the mean lateral, depth and elevation directions of the true US
images, so the three views are the B-mode plane, the view from the skin (C-plane) and the side view.

Input: poses.py-format exports of ONE sweep, e.g. written by scr_anchor.py track (<track>/poses/), by
tools/volume_pages.py (<pages>/<split>/poses/: system, classical, odometry on the same rows) or by
tools/slam_baseline.py evaluate. Rows without a pose in any of them are left out of all volumes.

  python tools/volume_figure.py --json runs/repro/volume3d/3XX/poses/fold0_run-316_scr-track.json \\
      --labels "no tracker (ours)" --rigid-fit --out runs/figures/volume_3XX_run-316.png

An estimate far from the truth (an outdated map, tens of cm off) makes the common grid huge and the volumes tiny:
--crop 40 keeps the grid on the true volume (+ 40 mm) and cuts off what falls outside (the share is printed).
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "baselines"))
from poses import accumulate, fan_mask, load_us, pixel_points  # noqa: E402

VIEWS = [(2, "B-mode plane (along the elevation)"), (1, "from the skin (along the depth)"), (0, "side (along the lateral axis)")]


def kabsch(P, Q):
    mp, mq = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - mp).T @ (Q - mq))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    T = np.eye(4)
    T[:3, :3] = Vt.T @ D @ U.T
    T[:3, 3] = mq - T[:3, :3] @ mp
    return T


def project(v, n, axis, centre, slab):
    """Slab maximum-intensity projection along axis (voxel units), NaN where no US data."""
    lo, hi = (0, v.shape[axis]) if slab <= 0 else (max(0, int(centre - slab / 2)), min(v.shape[axis], int(centre + slab / 2) + 1))
    sl = [slice(None)] * 3
    sl[axis] = slice(lo, hi)
    vv, nn = v[tuple(sl)].max(axis), n[tuple(sl)].max(axis)
    return np.where(nn > 0, vv, np.nan)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", nargs="+", required=True, help="exports of one sweep (all carry the true poses)")
    ap.add_argument("--labels", nargs="+", default=None, help="one per --json (default: the source name)")
    ap.add_argument("--rigid-fit", action="store_true", help="also each estimate after a rigid fit of the whole sweep")
    ap.add_argument("--out", required=True, help=".png (a .pdf is written next to it)")
    ap.add_argument("--root", default=None, help="data folder if the JSON's root is not valid here")
    ap.add_argument("--voxel", type=float, default=0.5, help="mm")
    ap.add_argument("--stride", type=int, default=2, help="US pixel stride")
    ap.add_argument("--slab", type=float, default=6.0, help="slab thickness (mm) of each projection; 0 = whole volume")
    ap.add_argument("--margin", type=float, default=3.0, help="mm")
    ap.add_argument("--crop", type=float, default=None,
                    help="mm: grid = the true volume + this margin; estimates outside it are cut off (for estimates "
                         "far off, e.g. an outdated map, which otherwise shrink the true volume to a dot)")
    ap.add_argument("--max-voxels", type=float, default=4e7)
    ap.add_argument("--fan-threshold", type=float, default=5.0)
    ap.add_argument("--title", default=None)
    args = ap.parse_args()

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    docs = [json.load(open(p)) for p in args.json]
    run = docs[0]["run"]
    if any(d["run"] != run for d in docs):
        raise SystemExit("all --json files must be the same sweep")
    if args.labels and len(args.labels) != len(docs):
        raise SystemExit("--labels needs one label per --json")
    labels = args.labels or [d["source"] for d in docs]
    root = Path(args.root) / run if args.root else Path(docs[0]["root"]) / run
    d0 = docs[0]
    roi, S = d0["us_roi"], np.asarray(d0["S_us_px_to_mm"])

    ok = lambda f: f["us"] and np.isfinite(f["T_world_us_pred"]).all() and np.isfinite(f["T_world_us_gt"]).all()
    byrow = [{f["row"]: f for f in d["frames"] if ok(f)} for d in docs]
    rows = sorted(set.intersection(*[set(b) for b in byrow]))
    if len(rows) < 10:
        raise SystemExit(f"only {len(rows)} rows with a pose in every export")
    frames = [byrow[0][r] for r in rows]
    T_gt = np.array([f["T_world_us_gt"] for f in frames])
    sources = [("true poses (Polaris)", T_gt, None)]

    mask = fan_mask(frames, root, roi, args.fan_threshold)
    r, c, P = pixel_points(mask, args.stride, S)
    _, _, P_err = pixel_points(mask, 16, S)
    gt_err = (T_gt @ P_err)[:, :3].transpose(0, 2, 1).reshape(-1, 3)
    for b, lab in zip(byrow, labels):
        T = np.array([b[x]["T_world_us_pred"] for x in rows])
        sources.append((lab, T, "estimate"))
        if args.rigid_fit:
            F = kabsch((T @ P_err)[:, :3].transpose(0, 2, 1).reshape(-1, 3), gt_err)
            sources.append((f"{lab}, rigid fit", F @ T, "fitted"))

    # grid along the mean US-image axes: lateral (image x), depth (image y), elevation (normal)
    cen = gt_err.mean(0)
    U, _, V = np.linalg.svd(T_gt[:, :3, :3].mean(0))
    Rm = U @ V                                               # closest rotation to the mean orientation
    if np.linalg.det(Rm) < 0:
        Rm[:, 2] *= -1
    Vt = Rm.T
    W = np.eye(4)
    W[:3, :3], W[:3, 3] = Vt, -Vt @ cen                     # world -> sweep frame
    corners = S @ np.array([[1, 1, 0, 1], [640, 1, 0, 1], [640, 480, 0, 1], [1, 480, 0, 1]], float).T
    allc = np.concatenate([(W @ T @ corners)[:, :3].transpose(0, 2, 1).reshape(-1, 3)
                           for _, T, _ in (sources[:1] if args.crop is not None else sources)])
    pad = args.margin if args.crop is None else args.crop
    lo, hi = allc.min(0) - pad, allc.max(0) + pad
    voxel = args.voxel
    while np.prod(np.ceil((hi - lo) / voxel)) > args.max_voxels:
        voxel *= 1.25
    shape = tuple(int(x) for x in np.ceil((hi - lo) / voxel))
    print(f"{run}: {len(frames)} frames, grid {shape} at {voxel:.2f} mm, {len(sources)} volumes", flush=True)

    imgs = [load_us(root / f["us"], roi)[r, c].astype(np.float32) for f in frames]
    vols = []
    for lab, T, kind in sources:
        s, n = np.zeros(shape, np.float32), np.zeros(shape, np.float32)
        dropped = 0
        for i in range(len(frames)):
            dropped += accumulate(s, n, lo, voxel, (W @ T[i] @ P)[:3].T, imgs[i])
        err = float(np.linalg.norm((T @ P_err - T_gt @ P_err)[:, :3], axis=1).mean()) if kind else 0.0
        vols.append((lab, np.where(n > 0, s / np.maximum(n, 1), 0), n, err, kind))
        cut = f", {100 * dropped / max(len(frames) * P.shape[1], 1):.0f} % of the pixels outside the grid" if dropped else ""
        print(f"  {lab:40s} mean pixel error {err:5.1f} mm{cut}", flush=True)
    vmax = float(np.percentile(vols[0][1][vols[0][2] > 0], 99.5)) or 1.0
    centre = ((W @ np.append(cen, 1))[:3] - lo) / voxel        # = the origin of the sweep frame
    slab = args.slab / voxel

    panels = [(lab, [project(v, n, a, centre[a], slab) for a, _ in VIEWS], err, kind) for lab, v, n, err, kind in vols]
    gt = panels[0][1]
    for lab, pr, err, kind in panels[1:]:                    # overlays: true green, estimate magenta
        ov = []
        for g, e in zip(gt, pr):
            gg, ee = np.nan_to_num(g / vmax).clip(0, 1), np.nan_to_num(e / vmax).clip(0, 1)
            ov.append(np.dstack([ee, gg, ee]))
        panels.append((f"overlay: true (green),\n{lab} (magenta)", ov, err, "overlay"))

    ext = [(hi - lo)[[b for b in range(3) if b != a]] for a, _ in VIEWS]
    widths = [e[0] for e in ext]
    fig, axs = plt.subplots(len(panels), 3, figsize=(10, 2.3 * len(panels)),
                            gridspec_kw={"width_ratios": widths}, squeeze=False)
    fig.patch.set_facecolor("white")
    for i, (lab, pr, err, kind) in enumerate(panels):
        for j, ((a, vname), im) in enumerate(zip(VIEWS, pr)):
            ax = axs[i, j]
            ax.set_facecolor("black")
            ex = ext[j]
            if im.ndim == 2:
                ax.imshow(im.T, cmap="gray", vmin=0, vmax=vmax, origin="lower", extent=[0, ex[0], 0, ex[1]], interpolation="nearest")
            else:
                ax.imshow(im.transpose(1, 0, 2), origin="lower", extent=[0, ex[0], 0, ex[1]], interpolation="nearest")
            ax.set_xticks([]), ax.set_yticks([])
            ax.plot([ex[0] * 0.05, ex[0] * 0.05 + 10], [ex[1] * 0.06] * 2, color="white", lw=2)   # 10 mm bar
            if i == 0:
                ax.set_title(vname, fontsize=9)
            if j == 0:
                ax.set_ylabel(lab + (f"\n{err:.1f} mm pixel error" if kind in ("estimate", "fitted") else ""), fontsize=8)
    fig.suptitle(args.title or f"{run}: compounded US volume (slab {args.slab:g} mm, bar 10 mm)", fontsize=10)
    fig.tight_layout(rect=(0, 0, 1, 1 - 0.35 / fig.get_figheight()))   # room for the title above the view names
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=200, facecolor="white")
    fig.savefig(out.with_suffix(".pdf"), facecolor="white")
    print(f"-> {out}, {out.with_suffix('.pdf')}")


if __name__ == "__main__":
    main()
