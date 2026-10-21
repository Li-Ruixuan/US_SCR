"""
Learning curves vs the label-noise floor: is the remaining error caused by the data, the
network, or the training? (supervisor question, note_RPR.md §6.1). No training, CPU only.

For each fold of the odometry arm and of the anchor network:
  * train vs validation translation error per epoch (median, mm), from history.json;
  * the label-noise floor: the error a perfect model would still show, because the labels
    themselves are noisy. Per step/pair: sqrt(sigma_a^2 + sigma_b^2 + (lever * angle)^2), where
    sigma is the tracker jitter of the two runs (from the raw 60 Hz pose.csv, an upper bound,
    as in inspect_data.py) and lever * angle is what a hand-eye lever-arm error of --lever-mm
    does to a step that rotates by `angle` (rad). Median over the held-out sweep's steps/pairs.
  * a reading per fold:
        train <= 1.5 x floor             -> at the floor: the labels limit (data)
        val >= 1.5 x train (end)         -> overfitting: too little / too narrow data
        otherwise                        -> underfitting: network or training
  * odometry only: does the validation loss move with the trajectory error across epochs?
    Spearman rank correlation per fold (loss vs final error; loss vs drift %).

  python tools/learning_curves.py                    # -> runs/diagnostics-loss/
  python tools/learning_curves.py --lever-mm 8       # smaller assumed hand-eye error
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eval import load_val_set                      # noqa: E402
from inspect_data import tracker_noise             # noqa: E402
from trajectory import gt_chains                   # noqa: E402


def spearman(a, b):
    ra, rb = np.argsort(np.argsort(a)), np.argsort(np.argsort(b))
    return float(np.corrcoef(ra, rb)[0, 1]) if len(a) > 2 else float("nan")


def jitter(root, run, cache):
    if run not in cache:
        s = tracker_noise(Path(root) / run, "mm")
        cache[run] = float(np.linalg.norm(s)) if s is not None else float("nan")
    return cache[run]


def reading(train_end, val_end, floor):
    if train_end <= 1.5 * floor:
        return "at the floor (data)"
    if val_end >= 1.5 * train_end:
        return "overfitting (data size/variety)"
    return "underfitting (network/training)"


def folds_of(arm):
    """Fold numbers that have a trained model in the arm folder."""
    return sorted(int(d.name[4:]) for d in Path(arm).glob("fold*") if (d / "history.json").exists())


def odometry(arm, lever, sig):
    rows = []
    for k in folds_of(arm):
        d = Path(arm) / f"fold{k}"
        c = json.load(open(d / "config.json"))
        h = [e for e in json.load(open(d / "history.json")) if "val_pair" in e]
        ds, _, val_runs = load_val_set({"args": c, "target_mean": c["target_mean"],
                                        "target_std": c["target_std"]})
        val_run = ",".join(val_runs)
        ang = np.concatenate([np.linalg.norm(ch["xi_gt"][:, 3:], axis=1) for ch in gt_chains(ds).values()])
        s = float(np.mean([jitter(c["root"], r, sig) for r in val_runs]))
        floor = float(np.median(np.sqrt(2 * s ** 2 + (lever * ang) ** 2)))
        tr = np.array([e["train"]["trans_mm_median"] for e in h])
        va = np.array([e["val_pair"]["trans_mm_median"] for e in h])
        vl = np.array([e["val_loss"] for e in h])
        fin = np.array([e["val_traj"]["final_mm_median"] for e in h])
        dr = np.array([e["val_traj"]["drift_pct_aggregate"] for e in h])
        rows.append({"fold": k, "sweep": val_run, "epochs": [e["epoch"] + 1 for e in h],
                     "train": tr.tolist(), "val": va.tolist(), "floor": floor, "jitter": s,
                     "train_end": float(tr[-1]), "val_end": float(va[-1]), "val_best": float(va.min()),
                     "reading": reading(tr[-1], va[-1], floor),
                     "rho_loss_final": spearman(vl, fin), "rho_loss_drift": spearman(vl, dr)})
        print(f"odometry fold {k} {val_run}: train {tr[-1]:.3f} | val {va[-1]:.3f} (best {va.min():.3f}) "
              f"| floor {floor:.3f} mm -> {rows[-1]['reading']} | loss~final rho {rows[-1]['rho_loss_final']:+.2f}",
              flush=True)
    return rows


def anchors(arm, pairs, lever, sig):
    P = json.load(open(pairs))["pairs"]
    rows = []
    for k in folds_of(arm):
        d = Path(arm) / f"fold{k}"
        c = json.load(open(d / "config.json"))
        h = json.load(open(d / "history.json"))
        val_runs = c.get("val_runs") or [c["val_run"]]
        val_run = ",".join(val_runs)
        root = c.get("root", "data/train")
        vp = [p for p in P if p["q_run"] in val_runs and p.get("kind", "scan") == "scan"]
        fl = [np.sqrt(jitter(root, p["q_run"], sig) ** 2 + jitter(root, p["key_run"], sig) ** 2
                      + (lever * np.radians(p["angle_deg"])) ** 2) for p in vp]
        floor = float(np.nanmedian(fl))
        tr = np.array([e["train"]["trans_mm_median"] for e in h])
        va = np.array([e["val"]["trans_mm_median"] for e in h])
        vl = np.array([e["val"]["loss"] for e in h])
        rows.append({"fold": k, "sweep": val_run, "epochs": [e["epoch"] + 1 for e in h],
                     "train": tr.tolist(), "val": va.tolist(), "floor": floor,
                     "train_end": float(tr[-1]), "val_end": float(va[-1]), "val_best": float(va.min()),
                     "reading": reading(tr[-1], va[-1], floor), "rho_loss_val_err": spearman(vl, va)})
        print(f"anchor   fold {k} {val_run}: train {tr[-1]:.1f} | val {va[-1]:.1f} (best {va.min():.1f}) "
              f"| floor {floor:.1f} mm -> {rows[-1]['reading']}", flush=True)
    return rows


def plot(rows, title, unit_fmt, path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(2, 4, figsize=(15, 6.6), sharex=True)
    for ax, r in zip(axs.flat, rows):
        ax.plot(r["epochs"], r["train"], "-o", color="#2a78d6", ms=3, lw=1.6, label="train")
        ax.plot(r["epochs"], r["val"], "-s", color="#eb6834", ms=3, lw=1.6, label="validation (held out)")
        ax.axhline(r["floor"], color="#6b6a64", ls=":", lw=1.2, label="label-noise floor")
        ax.set_title(f"fold {r['fold']} ({r['sweep']}): {r['reading']}", fontsize=9, loc="left")
        ax.set_ylim(0, None)
        ax.grid(True, color="#e4e3dc", lw=0.7)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axs[0, 0].legend(frameon=False, fontsize=8)
    for ax in axs[1]:
        ax.set_xlabel("epoch")
    for ax in axs[:, 0]:
        ax.set_ylabel(f"translation error, median ({unit_fmt})")
    fig.suptitle(title, x=0.01, ha="left", fontsize=12)
    fig.tight_layout()
    fig.savefig(path, dpi=140, facecolor="white")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--odometry", default="runs/rpr-rgb-gap4")
    ap.add_argument("--anchor", default="runs/anchor-rgbd-v2-reg")
    ap.add_argument("--pairs", default="runs/anchor-pairs/pairs_v2.json")
    ap.add_argument("--lever-mm", type=float, default=16.0,
                    help="assumed hand-eye lever-arm error (mm); 16 = the spread between calibration sessions")
    ap.add_argument("--out", default="runs/diagnostics-loss")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    sig = {}
    odo = odometry(args.odometry, args.lever_mm, sig)
    anc = anchors(args.anchor, args.pairs, args.lever_mm, sig)
    plot(odo, f"Odometry ({Path(args.odometry).name}): pair translation error per epoch vs label-noise floor",
         "mm per step", out / "odometry_curves.png")
    plot(anc, f"Anchor network ({Path(args.anchor).name}): keyframe-frame translation error per epoch vs floor",
         "mm per pair", out / "anchor_curves.png")

    md = ["# Learning curves vs label-noise floor", "",
          f"Floor = tracker jitter of both ends + hand-eye lever-arm error {args.lever_mm:g} mm x step rotation "
          "(median over the held-out sweep). Jitter is an upper bound, so the floor is too.", "",
          "## Odometry", "",
          "| fold | sweep | train (end) | val (end / best) | floor | val/train | reading | rho(val loss, final err) | rho(val loss, drift) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in odo:
        md.append(f"| {r['fold']} | {r['sweep']} | {r['train_end']:.3f} | {r['val_end']:.3f} / {r['val_best']:.3f} | "
                  f"{r['floor']:.3f} | {r['val_end'] / r['train_end']:.2f} | {r['reading']} | "
                  f"{r['rho_loss_final']:+.2f} | {r['rho_loss_drift']:+.2f} |")
    md += ["", "## Anchor network", "",
           "| fold | sweep | train (end) | val (end / best) | floor | val/train | reading | rho(val loss, val error) |",
           "|---|---|---|---|---|---|---|---|"]
    for r in anc:
        md.append(f"| {r['fold']} | {r['sweep']} | {r['train_end']:.1f} | {r['val_end']:.1f} / {r['val_best']:.1f} | "
                  f"{r['floor']:.1f} | {r['val_end'] / r['train_end']:.2f} | {r['reading']} | {r['rho_loss_val_err']:+.2f} |")
    md += ["", "Train error is measured on augmented windows/pairs. rho = Spearman rank correlation over epochs; "
           "near +1 means the loss tracks the trajectory goal."]
    (out / "learning_curves.md").write_text("\n".join(md) + "\n")
    json.dump({"lever_mm": args.lever_mm, "odometry": odo, "anchor": anc},
              open(out / "learning_curves.json", "w"), indent=1)
    print(f"wrote {out}/learning_curves.md, odometry_curves.png, anchor_curves.png")


if __name__ == "__main__":
    main()
