"""
Volume figures of the paper (fig:volume, fig:volume_snew, fig:volume_outdated in sn-article.tex): one sweep's US images compounded with the tracker poses
(grey, the reference) and with our poses (blue; red for an outdated map), on one grid per row, shown as one
slab projection with both volumes blended on white (multiply blend: grey where only the reference is, blue
where only ours is, dark where both agree) and the outline of each volume's footprint.

  fig3  same sweep, exam-view map vs generic map: (a) exam-view as placed, (b) generic as placed,
        (c) generic after the best rigid fit of the whole sweep (the "shape" error)
  fig4  2 x 2: one S-test sweep, one S-new sweep; columns as placed / after the rigid fit
  fig5  same sweep, the block's own map vs an outdated map, each with a strip of the per-frame inlier count
        (from the track's poses.npz) and the 400 gate dashed

The poses are the exports of scr_anchor.py track (<track>/poses/fold0_<run>_scr-track.json): the session
alignment of the evaluation (one per session), never a per-sweep fit, except in the "rigid fit" panels.
Errors are computed exactly as tools/us_analysis.py shape (5 US-image points, median over the sweep's frames)
and printed, so the annotations can show this sweep's values (default) or block values (--notes).

Training PC (needs the US images under the JSON's root), from the repository root:
  python paper/make_fig_volumes.py fig3 \
      --exam runs/track-v2map-5XXA-exam/poses/fold0_run-501_scr-track.json \
      --generic runs/track-v2map-5XXA-generic/poses/fold0_run-501_scr-track.json
  python paper/make_fig_volumes.py fig4 \
      --test runs/repro/track-v2map-3XX/poses/fold0_run-317_scr-track.json \
      --new runs/track-v2map-4XXC/poses/fold0_run-415_scr-track.json
  python paper/make_fig_volumes.py fig5 \
      --current runs/track-v2map-5XXC-exam/poses/fold0_run-517_scr-track.json \
      --outdated runs/track-v2map-5XXC-oldB/poses/fold0_run-517_scr-track.json \
      --current-npz runs/track-v2map-5XXC-exam/poses.npz --outdated-npz runs/track-v2map-5XXC-oldB/poses.npz

Output: paper/figures/<name>.png (300 dpi; --dpi) and a log of the numbers in paper/figures/<name>.txt.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "baselines"))
sys.path.insert(0, str(REPO))

OUT = Path(__file__).resolve().parent / "figures"
PX = np.array([[320, 240], [160, 120], [480, 120], [160, 400], [480, 400]], float)   # = tools/us_analysis.py
GREY, BLUE, RED = "#7f7f7f", "#2a78d6", "#d62728"   # blue = ours, as in make_fig_results.py
AXES = {"lateral": 0, "depth": 1, "elevation": 2}
# projection along one grid axis -> the two axes shown (x, y) and their names
VIEW = {1: ((0, 2), "skin"), 2: ((0, 1), "B-mode plane"), 0: ((2, 1), "side")}
GATE = 400


def rgb(h):
    return np.array([int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)])


def kabsch(P, Q):
    mp, mq = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - mp).T @ (Q - mq))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    T = np.eye(4)
    T[:3, :3] = Vt.T @ D @ U.T
    T[:3, 3] = mq - T[:3, :3] @ mp
    return T


# ---------------------------------------------------------------- data

class Sweep:
    """One or more pose exports of the same sweep, on the rows every export has a pose for."""

    def __init__(self, paths, root=None):
        self.docs = [json.load(open(p)) for p in paths]
        self.run = self.docs[0]["run"]
        if any(d["run"] != self.run for d in self.docs):
            raise SystemExit(f"not the same sweep: {[d['run'] for d in self.docs]}")
        self.root = Path(root) / self.run if root else Path(self.docs[0]["root"]) / self.run
        self.roi, self.S = self.docs[0]["us_roi"], np.asarray(self.docs[0]["S_us_px_to_mm"])
        ok = lambda f: f["us"] and np.isfinite(f["T_world_us_pred"]).all() and np.isfinite(f["T_world_us_gt"]).all()
        self.byrow = [{f["row"]: f for f in d["frames"] if ok(f)} for d in self.docs]
        self.n_frames = [sum(1 for f in d["frames"] if f["us"]) for d in self.docs]
        self.rows = sorted(set.intersection(*[set(b) for b in self.byrow]))
        if len(self.rows) < 10:
            raise SystemExit(f"{self.run}: only {len(self.rows)} rows with a pose in every export")
        self.frames = [self.byrow[0][r] for r in self.rows]
        self.T_gt = np.array([f["T_world_us_gt"] for f in self.frames])
        self.P5 = self.S @ np.stack([PX[:, 0], PX[:, 1], np.zeros(5), np.ones(5)])

    def est(self, i):
        return np.array([self.byrow[i][r]["T_world_us_pred"] for r in self.rows])

    def metrics(self, i):
        """As tools/us_analysis.py sweep_metrics, on all frames of export i with a pose (not only the common rows)."""
        fr = list(self.byrow[i].values())
        Tp = np.array([f["T_world_us_pred"] for f in fr])
        Tg = np.array([f["T_world_us_gt"] for f in fr])
        Xp, Xg = (Tp @ self.P5)[:, :3].transpose(0, 2, 1), (Tg @ self.P5)[:, :3].transpose(0, 2, 1)
        F = kabsch(Xp.reshape(-1, 3), Xg.reshape(-1, 3))
        Xf = Xp @ F[:3, :3].T + F[:3, 3]
        return {"absolute": float(np.median(np.linalg.norm(Xp - Xg, axis=2).mean(1))),
                "shape": float(np.median(np.linalg.norm(Xf - Xg, axis=2).mean(1))),
                "posed": len(fr) / max(self.n_frames[i], 1), "fit": F}

    def offset(self, T, W):
        """Mean offset of the 5 US points, estimate - reference, in the sweep frame (lateral, depth, elevation)."""
        d = (W @ T @ self.P5)[:, :3] - (W @ self.T_gt @ self.P5)[:, :3]
        return d.mean((0, 2))


def sweep_frame(sw):
    """World -> sweep frame: axes = mean lateral, depth, elevation of the reference US images, origin = centre."""
    pts = (sw.T_gt @ sw.P5)[:, :3].transpose(0, 2, 1).reshape(-1, 3)
    cen = pts.mean(0)
    U, _, V = np.linalg.svd(sw.T_gt[:, :3, :3].mean(0))
    R = U @ V
    if np.linalg.det(R) < 0:
        R[:, 2] *= -1
    W = np.eye(4)
    W[:3, :3], W[:3, 3] = R.T, -R.T @ cen
    return W


def compound(sw, Ts, W, args):
    """Compound the sweep with each pose set in Ts on one grid (the reference footprint + args.crop mm).
    Returns lo, hi, voxel and [(volume, count, % of pixels outside the grid)]."""
    from poses import accumulate, fan_mask, load_us, pixel_points
    mask = fan_mask(sw.frames, sw.root, sw.roi, args.fan_threshold)
    r, c, P = pixel_points(mask, args.stride, sw.S)
    corners = sw.S @ np.array([[1, 1, 0, 1], [640, 1, 0, 1], [640, 480, 0, 1], [1, 480, 0, 1]], float).T
    allc = (W @ sw.T_gt @ corners)[:, :3].transpose(0, 2, 1).reshape(-1, 3)
    lo, hi = allc.min(0) - args.crop, allc.max(0) + args.crop
    voxel = args.voxel
    while np.prod(np.ceil((hi - lo) / voxel)) > args.max_voxels:
        voxel *= 1.25
    shape = tuple(int(x) for x in np.ceil((hi - lo) / voxel))
    print(f"{sw.run}: {len(sw.frames)} frames, grid {shape} at {voxel:.2f} mm", flush=True)
    imgs = [load_us(sw.root / f["us"], sw.roi)[r, c].astype(np.float32) for f in sw.frames]
    out = []
    for T in Ts:
        s, n = np.zeros(shape, np.float32), np.zeros(shape, np.float32)
        dropped = sum(accumulate(s, n, lo, voxel, (W @ T[i] @ P)[:3].T, imgs[i]) for i in range(len(imgs)))
        out.append((np.where(n > 0, s / np.maximum(n, 1), 0), n, 100 * dropped / max(len(imgs) * P.shape[1], 1)))
    return lo, hi, voxel, out


def project(v, n, axis, lo, voxel, slab):
    """Slab maximum-intensity projection along axis, slab (mm) centred on the sweep-frame origin; and the footprint."""
    c = -lo[axis] / voxel
    a, b = (0, v.shape[axis]) if slab <= 0 else (max(0, int(c - slab / voxel / 2)), min(v.shape[axis], int(c + slab / voxel / 2) + 1))
    sl = [slice(None)] * 3
    sl[axis] = slice(a, b)
    vv, nn = v[tuple(sl)].max(axis), n[tuple(sl)].max(axis)
    foot = n.max(axis) > 0                               # whole-volume footprint, for the outline
    return np.where(nn > 0, vv, 0.0), foot


def pick_axis(view, offsets):
    """Projection axis: given, or 'auto' = the axis with the smallest mean offset over the shown estimates,
    so the larger two components of the displacement lie in the image."""
    if view != "auto":
        return {"skin": 1, "bmode": 2, "side": 0}[view]
    return int(np.argmin(np.abs(np.array(offsets)).max(0)))


# ---------------------------------------------------------------- drawing

def style():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "Liberation Sans", "DejaVu Sans"],
                         "font.size": 8, "pdf.fonttype": 42, "axes.linewidth": 0.5})
    return plt


def blend(ref, est, vmax, est_colour, gamma=0.7):
    g = (np.clip(ref / vmax, 0, 1) ** gamma)[..., None]
    e = (np.clip(est / vmax, 0, 1) ** gamma)[..., None]
    return (1 - g * (1 - rgb(GREY))) * (1 - e * (1 - rgb(est_colour)))


def panel(ax, ref, est, axis, lo, hi, voxel, vmax, colour, args, label=None, note=None, bar=True):
    (xa, ya), _ = VIEW[axis]
    (r, rf), (e, ef) = ref, est
    img = blend(r, e, vmax, colour)
    img = img.transpose(1, 0, 2) if xa < ya else img      # rows = y axis, columns = x axis
    if xa < ya:
        rf_, ef_ = rf.T, ef.T
    else:
        rf_, ef_ = rf, ef
    ext = [lo[xa], hi[xa], lo[ya], hi[ya]]
    ax.imshow(img, origin="lower", extent=ext, interpolation="nearest")
    xs = np.linspace(lo[xa], hi[xa], rf_.shape[1])
    ys = np.linspace(lo[ya], hi[ya], rf_.shape[0])
    ax.contour(xs, ys, rf_.astype(float), levels=[0.5], colors=[GREY], linewidths=0.5)
    ax.contour(xs, ys, ef_.astype(float), levels=[0.5], colors=[colour], linewidths=0.5)
    ax.set_xticks([]), ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    if args.depth_down and ya == 1:
        ax.invert_yaxis()
    if bar:
        x0, y0 = ext[0] + 0.06 * (ext[1] - ext[0]), ext[2] + 0.06 * (ext[3] - ext[2])
        if args.depth_down and ya == 1:
            y0 = ext[3] - 0.06 * (ext[3] - ext[2])
        ax.plot([x0, x0 + 10], [y0, y0], color="black", lw=1.5, solid_capstyle="butt")
        dy = 0.025 * (ext[3] - ext[2]) * (-1 if args.depth_down and ya == 1 else 1)     # clear of the bar
        ax.text(x0 + 5, y0 + dy, "10 mm", ha="center", va="bottom" if dy > 0 else "top", fontsize=6)
    if label:                                            # inside the top-left corner, clear of the title
        ax.text(0.02, 0.98, label, transform=ax.transAxes, fontweight="bold", fontsize=8, ha="left", va="top",
                bbox=dict(facecolor="white", edgecolor="none", pad=0.5))
    if note:                                             # under the panel, clear of the volume
        ax.set_xlabel(note, fontsize=6.5, labelpad=2)


def fmt(m, which, sweep_note=True):
    v = {"absolute": f"absolute {m['absolute']:.2f} mm", "shape": f"shape {m['shape']:.2f} mm"}[which]
    return v + ("\n(this sweep)" if sweep_note else "")


def legend(fig, items, y=0.005):
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor=c, edgecolor=c, label=l) for c, l in items], loc="lower center",
               ncol=len(items), frameon=False, fontsize=7, bbox_to_anchor=(0.5, y), handlelength=1.0, columnspacing=1.2)


def save(fig, name, log, args):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"{name}.png"
    fig.savefig(p, dpi=args.dpi, facecolor="white")
    (OUT / f"{name}.txt").write_text("\n".join(log) + "\n")
    print("\n".join(log))
    print(f"-> {p}, {OUT / (name + '.txt')}")


def notes_or(args, defaults):
    if args.notes is None:
        return defaults
    if len(args.notes) != len(defaults):
        raise SystemExit(f"--notes needs {len(defaults)} texts (use \\n for a line break)")
    return [n.replace("\\n", "\n") for n in args.notes]


# ---------------------------------------------------------------- figures

def fig3(args):
    plt = style()
    sw = Sweep([args.exam, args.generic], args.root)
    W = sweep_frame(sw)
    me, mg = sw.metrics(0), sw.metrics(1)
    Te, Tg = sw.est(0), sw.est(1)
    Tf = mg["fit"] @ Tg
    axis = pick_axis(args.view, [sw.offset(Te, W), sw.offset(Tg, W)])
    lo, hi, voxel, vols = compound(sw, [sw.T_gt, Te, Tg, Tf], W, args)
    pr = [project(v, n, axis, lo, voxel, args.slab) for v, n, _ in vols]
    vmax = float(np.percentile(vols[0][0][vols[0][1] > 0], 99.5)) or 1.0
    notes = notes_or(args, [fmt(me, "absolute"), fmt(mg, "absolute"), fmt(mg, "shape")])
    (xa, ya), vname = VIEW[axis]
    w = (hi - lo)[xa] * 3 / (hi - lo)[ya]
    fig, axs = plt.subplots(1, 3, figsize=(3.5, min(2.6, 3.5 / w + 0.55)))
    titles = ["Exam-view map", "Generic map, as placed", "Generic map, rigid fit"]
    for k, (ax, est, t, note) in enumerate(zip(axs, pr[1:], titles, notes)):
        panel(ax, pr[0], est, axis, lo, hi, voxel, vmax, BLUE, args, f"({'abc'[k]})", note, bar=True)
        ax.set_title(t, fontsize=7, pad=2)
    legend(fig, [(GREY, "tracker (reference)"), (BLUE, "ours")])
    fig.tight_layout(rect=(0, 0.13, 1, 0.95))
    log = [f"Figure 3: {sw.run}, view {vname} (projection along {list(AXES)[axis]}), slab {args.slab} mm",
           f"  exam-view map:  absolute {me['absolute']:.2f}  shape {me['shape']:.2f}  posed {100 * me['posed']:.0f} %  "
           f"offset (lat, depth, elev) {np.round(sw.offset(Te, W), 1)} mm",
           f"  generic map:    absolute {mg['absolute']:.2f}  shape {mg['shape']:.2f}  posed {100 * mg['posed']:.0f} %  "
           f"offset (lat, depth, elev) {np.round(sw.offset(Tg, W), 1)} mm",
           "  pixels outside the grid: " + ", ".join(f"{d:.0f} %" for _, _, d in vols[1:]),
           "  block means (S-ctrl table): exam-view 2.28 / 1.90, generic 13.57 / 3.79"]
    save(fig, "fig_volume_coverage", log, args)


def fig4(args):
    plt = style()
    rows = []
    for path, name in ((args.test, "S-test"), (args.new, "S-new")):
        sw = Sweep([path], args.root)
        W = sweep_frame(sw)
        m = sw.metrics(0)
        T = sw.est(0)
        axis = pick_axis(args.view, [sw.offset(T, W)])
        lo, hi, voxel, vols = compound(sw, [sw.T_gt, T, m["fit"] @ T], W, args)
        pr = [project(v, n, axis, lo, voxel, args.slab) for v, n, _ in vols]
        vmax = float(np.percentile(vols[0][0][vols[0][1] > 0], 99.5)) or 1.0
        rows.append((name, sw, W, m, T, axis, lo, hi, voxel, pr, vmax, vols))
    ratio = [(r[7] - r[6])[VIEW[r[5]][0][1]] / (r[7] - r[6])[VIEW[r[5]][0][0]] for r in rows]
    fig, axs = plt.subplots(2, 2, figsize=(3.5, 3.2), gridspec_kw={"height_ratios": ratio})
    defaults = []
    for name, sw, W, m, *_ in rows:
        defaults += [f"absolute {m['absolute']:.2f} mm", f"shape {m['shape']:.2f} mm"]
    notes = notes_or(args, defaults)
    log = ["Figure 4"]
    for i, (name, sw, W, m, T, axis, lo, hi, voxel, pr, vmax, vols) in enumerate(rows):
        for j, title in enumerate(("as placed", "after rigid fit")):
            ax = axs[i, j]
            panel(ax, pr[0], pr[1 + j], axis, lo, hi, voxel, vmax, BLUE, args, f"({'abcd'[2 * i + j]})", notes[2 * i + j])
            ax.set_title(f"{name}, {title}", fontsize=7, pad=2)
        log.append(f"  {name} {sw.run}: absolute {m['absolute']:.2f}  shape {m['shape']:.2f}  posed {100 * m['posed']:.0f} %  "
                   f"view {VIEW[axis][1]}  offset (lat, depth, elev) {np.round(sw.offset(T, W), 1)} mm  "
                   f"outside the grid {vols[1][2]:.0f} %")
    legend(fig, [(GREY, "tracker (reference)"), (BLUE, "ours")])
    fig.tight_layout(rect=(0, 0.075, 1, 0.97), h_pad=1.6)
    save(fig, "fig_volume_snew", log, args)


def inlier_strip(ax, npz, run, colour):
    z = np.load(npz)
    rows, inl, T = z[f"{run}_rows"], z[f"{run}_inl"].astype(float), z[f"{run}_T"]
    t = (rows - rows[0]) / 30.0
    ax.plot(t, np.maximum(inl, 1), color=colour, lw=0.5)
    ax.axhline(GATE, color="black", ls="--", lw=0.6)
    ax.set_yscale("log")
    ax.set_ylim(5, 5000)
    ax.set_yticks([10, 100, 1000])
    ax.set_yticklabels(["10", "100", "1000"], fontsize=6)
    ax.tick_params(axis="x", labelsize=6, length=2, pad=1)
    ax.tick_params(axis="y", length=2, pad=1)
    ax.set_xlabel("Time (s)", fontsize=6, labelpad=1)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    passed = float(np.mean(inl >= GATE))
    return float(np.median(inl)), passed, float(np.isfinite(T).all((1, 2)).mean())


def fig5(args):
    plt = style()
    sw = Sweep([args.current, args.outdated], args.root)
    W = sweep_frame(sw)
    mc, mo = sw.metrics(0), sw.metrics(1)
    Tc, To = sw.est(0), sw.est(1)
    axis = pick_axis(args.view, [sw.offset(Tc, W)]) if args.view == "auto" else pick_axis(args.view, [])
    lo, hi, voxel, vols = compound(sw, [sw.T_gt, Tc, To], W, args)
    pr = [project(v, n, axis, lo, voxel, args.slab) for v, n, _ in vols]
    vmax = float(np.percentile(vols[0][0][vols[0][1] > 0], 99.5)) or 1.0
    (xa, ya), vname = VIEW[axis]
    h_img = 1.75 * (hi - lo)[ya] / (hi - lo)[xa]
    fig, axs = plt.subplots(2, 2, figsize=(3.5, min(2.6, h_img + 0.95)),
                            gridspec_kw={"height_ratios": [max(h_img, 0.8), 0.42]})
    stats = [inlier_strip(axs[1, 0], args.current_npz, sw.run, BLUE), inlier_strip(axs[1, 1], args.outdated_npz, sw.run, RED)]
    axs[1, 0].set_ylabel("Inliers", fontsize=6, labelpad=1)
    defaults = []
    for m, (med, passed, _) in zip((mc, mo), stats):
        defaults.append(f"absolute {m['absolute']:.1f} mm\n{100 * passed:.0f} % pass the gate\nmedian {med:.0f} inliers")
    notes = notes_or(args, defaults)
    for k, (est, colour, title) in enumerate(((pr[1], BLUE, "Block's own map"), (pr[2], RED, args.outdated_title))):
        panel(axs[0, k], pr[0], est, axis, lo, hi, voxel, vmax, colour, args, f"({'ab'[k]})", notes[k])
        axs[0, k].set_title(title, fontsize=7, pad=2)
    legend(fig, [(GREY, "tracker (reference)"), (BLUE, "ours, current map"), (RED, "ours, outdated map")], y=0.0)
    fig.tight_layout(rect=(0, 0.06, 1, 0.94))
    log = [f"Figure 5: {sw.run}, view {vname}, slab {args.slab} mm"]
    for name, m, (med, passed, posed_raw), (_, _, out) in zip(("current", "outdated"), (mc, mo), stats, vols[1:]):
        log.append(f"  {name:9s} absolute {m['absolute']:.2f}  shape {m['shape']:.2f}  median inliers {med:.0f}  "
                   f"frames passing the {GATE} gate {100 * passed:.0f} % (raw poses {100 * posed_raw:.0f} %)  "
                   f"posed after smoothing {100 * m['posed']:.0f} %  outside the grid {out:.0f} %")
    log.append("  the volume uses the rows every export has a pose for (after smoothing)")
    save(fig, "fig_volume_outdated", log, args)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("fig3", "fig4", "fig5"):
        p = sub.add_parser(name)
        if name == "fig3":
            p.add_argument("--exam", required=True), p.add_argument("--generic", required=True)
        if name == "fig4":
            p.add_argument("--test", required=True), p.add_argument("--new", required=True)
        if name == "fig5":
            p.add_argument("--current", required=True), p.add_argument("--outdated", required=True)
            p.add_argument("--current-npz", required=True), p.add_argument("--outdated-npz", required=True)
            p.add_argument("--outdated-title", default="Outdated map (block B)")
        p.add_argument("--view", default="auto", choices=["auto", "skin", "bmode", "side"],
                       help="projection; auto = along the axis with the smallest displacement")
        p.add_argument("--slab", type=float, default=6.0, help="mm; 0 = whole volume")
        p.add_argument("--crop", type=float, default=20.0, help="mm around the reference volume")
        p.add_argument("--voxel", type=float, default=0.4)
        p.add_argument("--stride", type=int, default=2)
        p.add_argument("--max-voxels", type=float, default=4e7)
        p.add_argument("--fan-threshold", type=float, default=5.0)
        p.add_argument("--depth-down", action="store_true", help="draw the US depth axis pointing down")
        p.add_argument("--notes", nargs="+", default=None, help="annotation per panel instead of this sweep's values")
        p.add_argument("--root", default=None, help="data folder if the JSON's root is not valid here")
        p.add_argument("--dpi", type=int, default=600)
    args = ap.parse_args()
    {"fig3": fig3, "fig4": fig4, "fig5": fig5}[args.cmd](args)


if __name__ == "__main__":
    main()
