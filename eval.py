"""
Evaluate trained checkpoints on their held-out sweeps. Basic version.

  python eval.py --ckpts runs/rpr/fold*/best.pt
  python eval.py --ckpts runs/rpr/fold0/best.pt --per-segment

Each checkpoint knows its own fold (saved args), so its val sweep is rebuilt
exactly as in training. For every checkpoint:
  * zero-motion baseline and model, per pair AND per trajectory, side by side
  * drift curve: position error vs elapsed time since the segment start
Across checkpoints (leave-one-sweep-out): one row per held-out sweep, then
mean +- std over folds. Per-trajectory, never pooled over frames.

Writes eval.json, and unless --no-plot drift_curve.png plus one
traj_fold{k}_{sweep}.png per checkpoint (GT vs predicted path, error vs time),
next to the first ckpt or to --out.
"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader

from dataloader import (RPRConfig, RPRDataset, chain_config, load_hand_eye, split_runs,
                        test_sweeps)
from model import RPRNet
from trajectory import (compose, evaluate, gt_chains, predict, print_report,
                        zero_motion_preds)

HORIZONS_S = (0.5, 1.0, 2.0, 5.0, 10.0)


def drift_curve(chains, preds, horizons=HORIZONS_S):
    """Position error at fixed times after each segment start.
    Returns {h: array of errors (mm), one per segment long enough}."""
    out = {h: [] for h in horizons}
    for key, c in chains.items():
        T_p = compose(c["T_gt"][0], preds[key])
        err = np.linalg.norm(T_p[:, :3, 3] - c["T_gt"][:, :3, 3], axis=1)
        el = c["t"] - c["t"][0]
        for h in horizons:
            if el[-1] >= h:
                out[h].append(err[np.searchsorted(el, h)])
    return {h: np.asarray(v) for h, v in out.items()}


CALIB_CSV = Path(__file__).parent / "calib_matrix.csv"


def read_calib_csv(path=CALIB_CSV) -> np.ndarray:
    """TUS-REC calib_matrix.csv -> 4x4 map from US pixel (1-based, 640x480 grid) to marker (mm):
    spatial_calibration @ scaling_from_pixel_to_mm, as in the TUS-REC baseline read_calib_matrices."""
    rows = [l.strip().split(",") for l in open(path)]
    scaling = np.array(rows[1:5], float)
    rigid = np.array(rows[6:10], float)
    return rigid @ scaling


def us_points_px(calib_scaling_y: float) -> dict:
    """Named points on the US image, in 1-based calibration pixels: the probe contact (top of
    the probe arc, centre column) and 9 cm straight below it."""
    apex = (320.0, 65.0)
    return {"probe": apex, "depth_9cm": (apex[0], apex[1] + 90.0 / calib_scaling_y)}


def us_point_errors(chains, preds, T_marker_cam, calib=None):
    """Position error at points on the US image instead of the camera centre.
    T_cam_us = inv(T_marker_cam) @ calib; each point is carried by the true and the predicted
    camera trajectories. Returns {point: {"final_mm": [...per segment], "max_mm": [...]}}."""
    calib = read_calib_csv() if calib is None else calib
    sy = np.linalg.norm(calib[:3, 1])                   # mm per pixel along v
    P_cam = {n: np.linalg.inv(T_marker_cam) @ calib @ np.array([u, v, 0.0, 1.0])
             for n, (u, v) in us_points_px(sy).items()}
    out = {n: {"final_mm": [], "max_mm": []} for n in P_cam}
    for key, c in chains.items():
        T_gt, T_p = c["T_gt"], compose(c["T_gt"][0], preds[key])
        for n, p in P_cam.items():
            err = np.linalg.norm((T_p @ p)[:, :3] - (T_gt @ p)[:, :3], axis=1)
            out[n]["final_mm"].append(float(err[-1]))
            out[n]["max_mm"].append(float(err.max()))
    return out


def plot_trajectories(chains, preds, zero, path, title):
    """Per held-out sweep: top view (x-y), side view (x-z), and position error
    vs time. One colour per segment; solid = GT, dashed = model, both start at
    the GT start pose. The zero-motion error is drawn for reference."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.5))
    for n, (key, c) in enumerate(sorted(chains.items())):
        col = f"C{n % 10}"
        gt = c["T_gt"][:, :3, 3]
        pr = compose(c["T_gt"][0], preds[key])[:, :3, 3]
        zr = compose(c["T_gt"][0], zero[key])[:, :3, 3]
        for a, (i, j) in zip(ax[:2], [(0, 1), (0, 2)]):
            a.plot(gt[:, i], gt[:, j], "-", color=col, lw=1.2, label=f"seg {key[1]}" if i == 0 and j == 1 else None)
            a.plot(pr[:, i], pr[:, j], "--", color=col, lw=1.0)
            a.plot(gt[0, i], gt[0, j], "o", color=col, ms=4)
        el = c["t"] - c["t"][0]
        ax[2].plot(el, np.linalg.norm(pr - gt, axis=1), "-", color=col, lw=1.0)
        ax[2].plot(el, np.linalg.norm(zr - gt, axis=1), ":", color=col, lw=1.0)
    for a, (xl, yl) in zip(ax[:2], [("x", "y"), ("x", "z")]):
        a.set_xlabel(f"{xl} world (mm)")
        a.set_ylabel(f"{yl} world (mm)")
        a.set_aspect("equal", adjustable="datalim")
    ax[0].set_title("top view: solid GT, dashed model")
    ax[0].legend(fontsize=7)
    ax[1].set_title("side view")
    ax[2].set_title("position error: solid model, dotted zero motion")
    ax[2].set_xlabel("time since segment start (s)")
    ax[2].set_ylabel("error (mm)")
    ax[2].axhline(2.0, color="gray", lw=0.8, ls=":")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"wrote {path}")


def load_val_set(ck, test_root=None, test_runs=None):
    """The checkpoint's validation sweep(s) as a chain dataset, exactly as in training;
    with test_root, the sweeps of that folder instead (test_runs, or every run-* there).
    Returns (ds, T_marker_cam, runs)."""
    a = ck["args"]
    mean, std = np.asarray(ck["target_mean"]), np.asarray(ck["target_std"])
    T_mc = load_hand_eye(a["hand_eye"], a["hand_eye_units"]) if a["hand_eye"] else np.eye(4)
    if test_root:
        root, val_runs, scans = test_root, test_sweeps(test_root, test_runs), []
    else:
        root, scans = a["root"], a["scan_runs"]
        _, val_runs = split_runs(root, scans, a["fold"], a.get("val_runs"))
    cfg = RPRConfig(T_marker_cam=T_mc, seq_len=a["seq_len"], frame_gap=a["frame_gap"],
                    use_depth=a["use_depth"], use_us=a["use_us"],
                    rgb_from_us=a.get("rgb_from_us", False),
                    use_rgb=not a.get("no_rgb", False),
                    image_size=tuple(a["image_size"]),
                    us_size=tuple(a.get("us_size", (256, 256))),   # runs before 2026-09-30 used 256x256
                    max_step_s=a["max_step_s"],
                    spike_factor=a["spike_factor"], target_mean=mean, target_std=std)
    ds = RPRDataset(root, val_runs, scans, chain_config(cfg))
    return ds, T_mc, val_runs


def predict_ckpt(ck, ds, device, batch_size, workers):
    """Model predictions {(run, seg): (N-1, 6) xi in mm|rad} on a chain dataset."""
    a = ck["args"]
    mean, std = np.asarray(ck["target_mean"]), np.asarray(ck["target_std"])
    dl = DataLoader(ds, batch_size, shuffle=False, num_workers=workers)
    net = RPRNet(use_depth=a["use_depth"], use_us=a["use_us"], pretrained=False,
                 corr_radius=a["corr_radius"], use_dt=a["use_dt"],
                 temporal=a.get("temporal", "none"), us_mode=a.get("us_mode", "vector"),
                 use_rgb=not a.get("no_rgb", False)).to(device)
    net.load_state_dict(ck["model"])
    preds, _ = predict(net, dl, device, mean, std)
    return preds


def read_calib_parts(path=CALIB_CSV):
    """calib_matrix.csv -> (rigid, scaling): rigid maps the US image plane (mm) to the
    marker (mm); scaling maps 1-based calibration pixels (640x480 grid) to image mm."""
    rows = [l.strip().split(",") for l in open(path)]
    return np.array(rows[6:10], float), np.array(rows[1:5], float)


def cached_preds(ckpt_path, ck, ds, device, batch_size, workers, tag=""):
    """Model predictions, cached next to the arm in <arm>/preds/fold<k>[_<tag>].npz so the
    network runs once for eval, diagnostics and pose export (tag: test folder name).
    The cache is ignored if best.pt is newer."""
    cache = Path(ckpt_path).parent.parent / "preds" / f"fold{ck['args']['fold']}{'_' + tag if tag else ''}.npz"
    if cache.exists() and cache.stat().st_mtime >= Path(ckpt_path).stat().st_mtime:
        z = np.load(cache, allow_pickle=True)
        return {(str(r), int(s)): v for (r, s), v in zip(z["keys"], z["values"])}
    preds = predict_ckpt(ck, ds, device, batch_size, workers)
    keys = list(preds)
    values = np.empty(len(keys), dtype=object)
    values[:] = [preds[k] for k in keys]
    cache.parent.mkdir(parents=True, exist_ok=True)
    np.savez(cache, keys=np.array(keys, dtype=object), values=values)
    return preds


def eval_ckpt(path, device, batch_size, workers, per_segment, plot_dir=None,
              test_root=None, test_runs=None):
    ck = torch.load(path, map_location=device, weights_only=False)
    a = ck["args"]
    ds, T_mc, val_runs = load_val_set(ck, test_root, test_runs)
    tag = Path(test_root).name if test_root else ""
    print(f"\n=== {path}  (fold {a['fold']}, epoch {ck['epoch'] + 1}, "
          f"{'test ' + tag if tag else 'val'} {val_runs})")

    chains = gt_chains(ds)
    preds = cached_preds(path, ck, ds, device, batch_size, workers, tag)
    zero = zero_motion_preds(chains)
    res_zero, res_model = evaluate(chains, zero), evaluate(chains, preds)
    print_report(res_zero, "zero-motion baseline:")
    print_report(res_model, "model:", per_segment=per_segment)

    dz, dm = drift_curve(chains, zero), drift_curve(chains, preds)
    print("  drift curve, median position error (mm) vs time since segment start:")
    for h in HORIZONS_S:
        if len(dm[h]):
            print(f"    {h:5.1f}s  model {np.median(dm[h]):7.2f}   zero {np.median(dz[h]):7.2f}"
                  f"   (n={len(dm[h])} segments)")
    us_pts = None
    if CALIB_CSV.exists():
        us_pts = {"model": us_point_errors(chains, preds, T_mc),
                  "zero": us_point_errors(chains, zero, T_mc)}
        print("  error at the US image (median over segments, final / max, mm):")
        for n in us_pts["model"]:
            m, z = us_pts["model"][n], us_pts["zero"][n]
            print(f"    {n:10s} model {np.median(m['final_mm']):7.2f} / {np.median(m['max_mm']):7.2f}"
                  f"   zero {np.median(z['final_mm']):7.2f} / {np.median(z['max_mm']):7.2f}")
    if not a["hand_eye"]:
        print("  NO HAND-EYE at training time: not reportable")
    if a["use_us"]:
        print("  US model: PRELIMINARY -- one subject, same anatomy; needs a held-out subject")
    per_run = {}                                  # the same numbers per sweep
    if len(val_runs) > 1:
        print("  per sweep (model vs zero motion): pair mm | pair deg | final mm | US final mm")
        for run in val_runs:
            c = {k: v for k, v in chains.items() if k[0] == run}
            if not c:
                continue
            p = {k: v for k, v in preds.items() if k in c}
            z = {k: v for k, v in zero.items() if k in c}
            rm, rz = evaluate(c, p), evaluate(c, z)
            um = float(np.median(us_point_errors(c, p, T_mc)["depth_9cm"]["final_mm"])) if us_pts else float("nan")
            uz = float(np.median(us_point_errors(c, z, T_mc)["depth_9cm"]["final_mm"])) if us_pts else float("nan")
            per_run[run] = {"model": rm, "zero": rz, "us_final_mm": um, "us_final_mm_zero": uz}
            print(f"    {run:10s} {rm['pair']['trans_mm_median']:.3f} / {rz['pair']['trans_mm_median']:.3f} | "
                  f"{rm['pair']['rot_deg_median']:.3f} / {rz['pair']['rot_deg_median']:.3f} | "
                  f"{rm['summary']['final_mm_median']:.1f} / {rz['summary']['final_mm_median']:.1f} | "
                  f"{um:.1f} / {uz:.1f}")
    if plot_dir is not None:
        plot_trajectories(chains, preds, zero,
                          Path(plot_dir) / f"traj_fold{a['fold']}_{tag + '_' if tag else ''}{'_'.join(val_runs)}.png",
                          f"fold {a['fold']}, {'test' if tag else 'held-out'} {', '.join(val_runs)}, epoch {ck['epoch'] + 1}")
    return {"ckpt": str(path), "fold": a["fold"], "val_runs": val_runs, "test_root": test_root,
            "per_run": per_run,
            "preliminary_us": bool(a["use_us"]), "hand_eye": a["hand_eye"],
            "us_points": us_pts,
            "model": res_model, "zero": res_zero,
            "drift_curve": {str(h): v.tolist() for h, v in dm.items()},
            "drift_curve_zero": {str(h): v.tolist() for h, v in dz.items()}}


def plot_drift(results, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(6, 4))
    for key, style, label in [("drift_curve", "-o", "model"),
                              ("drift_curve_zero", "--x", "zero motion")]:
        hs, med = [], []
        for h in HORIZONS_S:
            v = np.concatenate([np.asarray(r[key][str(h)]) for r in results])
            if len(v):
                hs.append(h)
                med.append(np.median(v))
        ax.plot(hs, med, style, label=label)
    ax.axhline(2.0, color="gray", lw=0.8, ls=":", label="2 mm threshold")
    ax.set_xlabel("time since segment start (s)")
    ax.set_ylabel("median position error (mm)")
    ax.set_title("unanchored drift, all folds")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=110)
    plt.close(fig)
    print(f"wrote {path}")


def ablation_table(run_dirs, out=None):
    """Compare arms from their eval.json (written by run_folds.sh / eval.py).
    Per held-out sweep and arm: pair error relative to that sweep's zero motion,
    final error and aggregate drift, then the mean over sweeps and the drift curve
    (median position error over all segments of all folds)."""
    arms = {Path(d).name: {",".join(r["val_runs"]): r
                           for r in json.load(open(Path(d) / "eval.json"))}
            for d in run_dirs}
    sweeps = sorted(set().union(*arms.values()))
    rel = lambda m, z: 100 * (m / z - 1)
    table = {}
    print("\n=== ABLATION (best.pt of each fold; pair % is relative to that sweep's zero motion)")
    for sw in sweeps:
        z = next(a[sw]["zero"] for a in arms.values() if sw in a)
        print(f"\n  {sw}  zero motion: pair {z['pair']['trans_mm_median']:.3f} mm "
              f"{z['pair']['rot_deg_median']:.3f} deg | final {z['summary']['final_mm_median']:.1f} mm "
              f"| drift {z['summary']['drift_pct_aggregate']:.1f}%")
        for name, a in arms.items():
            if sw not in a:
                print(f"    {name:24s} (missing)")
                continue
            m, zz = a[sw]["model"], a[sw]["zero"]
            row = {"trans_pct": rel(m["pair"]["trans_mm_median"], zz["pair"]["trans_mm_median"]),
                   "rot_pct": rel(m["pair"]["rot_deg_median"], zz["pair"]["rot_deg_median"]),
                   "final_mm": m["summary"]["final_mm_median"],
                   "final_ratio": m["summary"]["final_mm_median"] / zz["summary"]["final_mm_median"],
                   "drift_pct": m["summary"]["drift_pct_aggregate"],
                   "drift_vs_zero": m["summary"]["drift_pct_aggregate"] - zz["summary"]["drift_pct_aggregate"]}
            table.setdefault(name, {})[sw] = row
            print(f"    {name:24s} pair {row['trans_pct']:+5.0f}% / {row['rot_pct']:+5.0f}% | "
                  f"final {row['final_mm']:6.1f} mm | drift {row['drift_pct']:5.1f}%")
    print("\n  MEAN over sweeps [95% bootstrap CI over sweeps]")
    print("    arm                      pair trans           pair rot             final/zero         beats zero drift")
    summary = {}
    rng = np.random.default_rng(0)
    for name, rows in table.items():
        v = list(rows.values())
        s = {k: float(np.mean([r[k] for r in v])) for k in v[0]}
        s["beats_zero_drift"] = f"{sum(r['drift_vs_zero'] < 0 for r in v)}/{len(v)}"
        idx = rng.integers(0, len(v), (2000, len(v)))       # resample held-out sweeps
        for k in ("trans_pct", "rot_pct", "final_ratio", "drift_vs_zero"):
            x = np.array([r[k] for r in v])[idx].mean(1)
            s[k + "_ci"] = [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]
        summary[name] = s
        ci = lambda k, f: f"{s[k]:{f}} [{s[k + '_ci'][0]:{f}}, {s[k + '_ci'][1]:{f}}]"
        print(f"    {name:24s} {ci('trans_pct', '+.0f')}%   {ci('rot_pct', '+.0f')}%   "
              f"{ci('final_ratio', '.2f')}   {s['beats_zero_drift']}")
    print("    (8 sweeps of one subject: the CI shows the spread between sweeps, not across subjects)")
    print("\n  DRIFT CURVE: median position error (mm) over all segments, by time since segment start")
    print("    " + " " * 24 + "".join(f"{h:>8.1f}s" for h in HORIZONS_S))
    curves = {}
    first = next(iter(arms.values()))
    for name, a in [("zero motion", first)] + list(arms.items()):
        key = "drift_curve_zero" if name == "zero motion" else "drift_curve"
        med = []
        for h in HORIZONS_S:
            v = np.concatenate([np.asarray(r[key][str(h)]) for r in a.values()])
            med.append(float(np.median(v)) if len(v) else float("nan"))
        curves[name] = med
        print(f"    {name:24s}" + "".join(f"{x:9.2f}" for x in med))
    if out is not None:
        out = Path(out)
        out.mkdir(parents=True, exist_ok=True)
        labels = {Path(d).name: arm_label(d) for d in run_dirs}
        json.dump({"per_sweep": table, "mean": summary, "drift_curve": curves,
                   "horizons_s": list(HORIZONS_S), "labels": labels},
                  open(out / "ablation.json", "w"), indent=2)
        write_ablation_tables(table, summary, curves, labels, arms, out)
        plot_ablation(summary, curves, labels, out / "ablation.png")
        print(f"\nwrote {out / 'ablation.json'}, ablation.md, ablation.csv, ablation.png")


def arm_label(run_dir):
    """Inputs ('RGB', 'RGB + D', 'US only', ...) from the run's saved args, plus whatever
    differs from the reference setting (gap 4, reversal 0.5, all sweeps)."""
    c = json.load(open(sorted(Path(run_dir).glob("fold*/config.json"))[0]))
    lab = ("US only" if c.get("rgb_from_us") else
           "RGB" + (" + D" if c["use_depth"] else "") + (" + US" if c["use_us"] else ""))
    if c.get("frame_gap", 4) != 4:
        lab += f", gap {c['frame_gap']}"
    if c.get("reverse_prob", 0.5) == 0:
        lab += ", no reversal"
    if c.get("max_train_sweeps"):
        lab += f", {c['max_train_sweeps']} train sweeps"
    if c.get("include_val"):
        lab += ", UPPER BOUND"
    return lab


def write_ablation_tables(table, summary, curves, labels, arms, out):
    """ablation.md (readable) and ablation.csv (one row per sweep x arm)."""
    names = list(table)
    sweeps = sorted(set().union(*arms.values()))
    md = ["# Ablation (best.pt per fold; % relative to that sweep's zero motion)", "",
          "## Mean over held-out sweeps [95 % bootstrap CI over sweeps]", "",
          "| Arm | Pair trans | Pair rot | Final error vs zero | Drift vs zero | Sweeps beating zero drift |",
          "|---|---|---|---|---|---|"]
    for n in names:
        s = summary[n]
        c = lambda k, f: f"{s[k]:{f}} [{s[k + '_ci'][0]:{f}}, {s[k + '_ci'][1]:{f}}]"
        md.append(f"| {labels[n]} | {c('trans_pct', '+.0f')} % | {c('rot_pct', '+.0f')} % | "
                  f"{c('final_ratio', '.2f')}× | {c('drift_vs_zero', '+.1f')} pts | {s['beats_zero_drift']} |")
    md += ["", "The CI resamples the 8 held-out sweeps (one subject): it shows the spread between sweeps, "
           "not the uncertainty across subjects."]
    md += ["", "## Drift curve: median position error (mm) by time since segment start", "",
           "| | " + " | ".join(f"{h:g} s" for h in HORIZONS_S) + " |",
           "|---|" + "---|" * len(HORIZONS_S)]
    for n, med in curves.items():
        md.append(f"| {labels.get(n, n)} | " + " | ".join(f"{x:.1f}" for x in med) + " |")
    md += ["", "## Per held-out sweep: pair trans / rot vs zero, final error (mm), drift (%)", "",
           "| Sweep | zero motion (final, drift) | " + " | ".join(labels[n] for n in names) + " |",
           "|---|---|" + "---|" * len(names)]
    for sw in sweeps:
        z = next(a[sw]["zero"]["summary"] for a in arms.values() if sw in a)
        cells = [f"{table[n][sw]['trans_pct']:+.0f} / {table[n][sw]['rot_pct']:+.0f} %, "
                 f"{table[n][sw]['final_mm']:.1f} mm, {table[n][sw]['drift_pct']:.1f} %"
                 if sw in table[n] else "—" for n in names]
        md.append(f"| {sw} | {z['final_mm_median']:.1f} mm, {z['drift_pct_aggregate']:.1f} % | "
                  + " | ".join(cells) + " |")
    (out / "ablation.md").write_text("\n".join(md) + "\n")
    rows = ["arm,sweep,pair_trans_pct,pair_rot_pct,final_mm,final_ratio,drift_pct,drift_vs_zero"]
    for n in names:
        for sw, r in table[n].items():
            rows.append(f"{labels[n]},{sw},{r['trans_pct']:.2f},{r['rot_pct']:.2f},{r['final_mm']:.2f},"
                        f"{r['final_ratio']:.3f},{r['drift_pct']:.2f},{r['drift_vs_zero']:.2f}")
    (out / "ablation.csv").write_text("\n".join(rows) + "\n")


ARM_STYLE = {"RGB": ("#2a78d6", "o"), "RGB + D": ("#eb6834", "s"),
             "RGB + US": ("#1baf7a", "^"), "RGB + D + US": ("#eda100", "D")}
EXTRA_STYLE = [("#e87ba4", "v"), ("#008300", "P"), ("#4a3aa7", "X"), ("#e34948", "*")]


def arm_styles(names, labels):
    """Fixed colours for the four input arms; other arms (gap, reversal, US only, ...)
    take the next palette slots in the order given. More than 8 arms: split the table."""
    out, k = {}, 0
    for n in names:
        if labels[n] in ARM_STYLE:
            out[n] = ARM_STYLE[labels[n]]
        else:
            out[n] = EXTRA_STYLE[k % len(EXTRA_STYLE)]
            k += 1
    return out


def plot_ablation(summary, curves, labels, path):
    """Left: drift curve per arm vs zero motion. Right: mean change vs zero motion
    for pair translation, pair rotation and final error, bars coloured by arm."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ink, muted, grid = "#1f1f1e", "#6b6a64", "#e4e3dc"
    plt.rcParams.update({"font.size": 10, "axes.edgecolor": muted, "axes.labelcolor": ink,
                         "xtick.color": muted, "ytick.color": muted, "text.color": ink})
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 4.6), gridspec_kw={"width_ratios": [1.15, 1]})
    names = [n for n in labels if n in summary]
    names.sort(key=lambda n: list(ARM_STYLE).index(labels[n]) if labels[n] in ARM_STYLE else len(ARM_STYLE))
    style = arm_styles(names, labels)

    x = np.asarray(HORIZONS_S)
    a1.plot(x, curves["zero motion"], "--", color="#8f8e86", lw=2, label="zero motion")
    for n in names:
        col, mk = style[n]
        a1.plot(x, curves[n], "-", color=col, lw=2, marker=mk, ms=7, label=labels[n],
                markeredgecolor="white", markeredgewidth=1.5)
    a1.axhline(2.0, color=muted, lw=0.8, ls=":")
    a1.annotate("2 mm target", (x[-1] * 1.08, 2.0), xytext=(0, 4), textcoords="offset points",
                color=muted, fontsize=8)
    a1.set_xscale("log")
    a1.set_xticks(x)
    a1.set_xticklabels([f"{h:g}" for h in x])
    a1.set_xlim(x[0] * 0.85, x[-1] * 1.9)
    a1.set_xlabel("time since segment start (s)")
    a1.set_ylabel("median position error (mm)")
    a1.set_title("Drift: median position error over all 8 held-out sweeps", loc="left", fontsize=11)
    a1.grid(True, color=grid, lw=0.8)
    a1.legend(frameon=False, fontsize=9, loc="upper left")

    metrics = [("trans_pct", "pair translation"), ("rot_pct", "pair rotation"),
               ("final_ratio", "final error")]
    w = 0.8 / len(names)
    for i, n in enumerate(names):
        col, _ = style[n]
        vals = [summary[n][k] if k != "final_ratio" else 100 * (summary[n][k] - 1)
                for k, _ in metrics]
        pos = np.arange(len(metrics)) + (i - (len(names) - 1) / 2) * w
        bars = a2.bar(pos, vals, w * 0.92, color=col, label=labels[n], zorder=3)
        for b, v in zip(bars, vals):
            a2.annotate(f"{v:.0f}", (b.get_x() + b.get_width() / 2, v), xytext=(0, -3),
                        textcoords="offset points", ha="center", va="top", fontsize=8, color=ink)
    a2.axhline(0, color=muted, lw=1)
    a2.set_xticks(np.arange(len(metrics)))
    a2.set_xticklabels([m for _, m in metrics])
    a2.set_ylabel("change vs zero motion (%), lower is better")
    a2.set_title("Mean over 8 held-out sweeps", loc="left", fontsize=11)
    a2.grid(True, axis="y", color=grid, lw=0.8, zorder=0)
    a2.legend(frameon=False, fontsize=9, loc="lower right")
    for a in (a1, a2):
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
    fig.suptitle("Ablation of input modalities (gap 4, one subject; US preliminary)",
                 x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=150, facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpts", nargs="+")
    ap.add_argument("--ablation", nargs="+", metavar="RUN_DIR",
                    help="compare arms from their eval.json instead of evaluating checkpoints")
    ap.add_argument("--batch-size", type=int, default=8)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--per-segment", action="store_true")
    ap.add_argument("--no-plot", action="store_true")
    ap.add_argument("--out", default=None, help="output folder (default: first ckpt's folder)")
    ap.add_argument("--test-root", default=None,
                    help="evaluate on the sweeps of this folder instead of the validation sweeps")
    ap.add_argument("--test-runs", nargs="+", default=None, help="with --test-root: only these (default: every run-*)")
    args = ap.parse_args()
    if args.ablation:
        ablation_table(args.ablation, args.out)
        return
    if not args.ckpts:
        ap.error("give --ckpts or --ablation")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    out = Path(args.out) if args.out else Path(args.ckpts[0]).parent
    out.mkdir(parents=True, exist_ok=True)
    results = [eval_ckpt(p, device, args.batch_size, args.workers, args.per_segment,
                         None if args.no_plot else out, args.test_root, args.test_runs)
               for p in args.ckpts]

    print("\n=== SUMMARY (one row per evaluated sweep)")
    print("  sweep       pair mm   pair deg   traj final mm   drift agg %   (zero: drift agg %)")
    cols = []
    for r in results:
        rows = r["per_run"].items() if r["per_run"] else [(",".join(r["val_runs"]), r)]
        for name, x in rows:
            p, s, z = x["model"]["pair"], x["model"]["summary"], x["zero"]["summary"]
            row = [p["trans_mm_median"], p["rot_deg_median"], s["final_mm_median"],
                   s["drift_pct_aggregate"]]
            cols.append(row)
            print(f"  {name:10s} {row[0]:8.3f} {row[1]:10.3f} {row[2]:15.2f} "
                  f"{row[3]:13.1f}   ({z['drift_pct_aggregate']:.1f})")
    if len(cols) > 1:
        c = np.asarray(cols)
        m, sd = c.mean(0), c.std(0, ddof=1)
        print(f"  {'mean+-std':10s} {m[0]:.3f}+-{sd[0]:.3f} {m[1]:.3f}+-{sd[1]:.3f} "
              f"{m[2]:.2f}+-{sd[2]:.2f} {m[3]:.1f}+-{sd[3]:.1f}")

    json.dump(results, open(out / "eval.json", "w"), indent=2)
    print(f"wrote {out / 'eval.json'}")
    if not args.no_plot:
        plot_drift(results, out / "drift_curve.png")


if __name__ == "__main__":
    main()
