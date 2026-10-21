"""
Error by motion type (task 4, note_RPR.md §6.1). No training, CPU only; uses the cached
odometry predictions (<arm>/preds/fold<k>.npz, written by eval.py).

Every step of every held-out sweep is labelled from its GROUND-TRUTH motion:
    still             |t| < --still-mm and angle < --still-deg (about the tracker noise)
    turn              rotation moves the US image more than the translation does:
                      angle (rad) x --lever-mm > |t|
    straight-forward  translation-dominated, mostly along the camera's viewing axis (|tz| largest)
    straight-sideways translation-dominated, mostly across it (|tx| or |ty| largest)
For each type: share of steps, and the median per-step error of the model vs zero motion
(translation of the step in mm, rotation in deg), so it shows where the model fails.

  python tools/motion_analysis.py                         # odometry arm rpr-rgb-gap4
  python tools/motion_analysis.py --arm runs/rpr-rgbd-gap4 --out runs/motion-analysis-rgbd
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from eval import load_val_set                      # noqa: E402
from geometry import se3_exp                       # noqa: E402
from trajectory import gt_chains                   # noqa: E402

TYPES = ["still", "turn", "straight-forward", "straight-sideways"]


def step_errors(xi_p, xi_g):
    Tp, Tg = se3_exp(xi_p), se3_exp(xi_g)
    t_err = np.linalg.norm(Tp[:, :3, 3] - Tg[:, :3, 3], axis=1)
    R = np.swapaxes(Tg[:, :3, :3], 1, 2) @ Tp[:, :3, :3]
    r_err = np.degrees(np.arccos(np.clip((np.trace(R, axis1=1, axis2=2) - 1) / 2, -1, 1)))
    return t_err, r_err, Tg[:, :3, 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="runs/rpr-rgb-gap4")
    ap.add_argument("--still-mm", type=float, default=0.3)
    ap.add_argument("--still-deg", type=float, default=0.1)
    ap.add_argument("--lever-mm", type=float, default=190.0,
                    help="camera to US image distance used to compare rotation with translation")
    ap.add_argument("--out", default="runs/motion-analysis")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    folds = sorted(int(f.stem[4:]) for f in (Path(args.arm) / "preds").glob("fold*.npz")
                   if f.stem[4:].isdigit())             # skip test-set caches (fold0_<test>.npz)
    if not folds:
        raise SystemExit(f"no {args.arm}/preds/fold*.npz: run eval.py on the arm first")
    rows = []                                       # one per step
    for k in folds:
        d = Path(args.arm) / f"fold{k}"
        c = json.load(open(d / "config.json"))
        ds, _, val_runs = load_val_set({"args": c, "target_mean": c["target_mean"],
                                        "target_std": c["target_std"]})
        z = np.load(Path(args.arm) / "preds" / f"fold{k}.npz", allow_pickle=True)
        preds = {(str(r), int(s)): v for (r, s), v in zip(z["keys"], z["values"])}
        for key, ch in gt_chains(ds).items():
            xg, xp = ch["xi_gt"], preds[key]
            t_err, r_err, t = step_errors(xp, xg)
            zt, zr, _ = step_errors(np.zeros_like(xg), xg)          # zero motion = the step itself
            ang = np.linalg.norm(xg[:, 3:], axis=1)
            tn = np.linalg.norm(t, axis=1)
            for i in range(len(xg)):
                if tn[i] < args.still_mm and np.degrees(ang[i]) < args.still_deg:
                    typ = "still"
                elif ang[i] * args.lever_mm > tn[i]:
                    typ = "turn"
                elif np.argmax(np.abs(t[i])) == 2:
                    typ = "straight-forward"
                else:
                    typ = "straight-sideways"
                rows.append((key[0], typ, t_err[i], r_err[i], zt[i], zr[i]))
        print(f"fold {k} {val_runs}: done", flush=True)

    sweeps = sorted({r[0] for r in rows})
    res = {"by_type": {}, "by_sweep": {}}
    md = ["# Odometry error by motion type", "",
          f"Arm: {Path(args.arm).name}. Ground-truth step labels: still (< {args.still_mm:g} mm and "
          f"< {args.still_deg:g} deg), turn (rotation x {args.lever_mm:g} mm > translation), straight "
          "(translation-dominated; forward = mostly along the camera axis). Median per-step error; "
          "zero motion's error is the step itself.", "",
          "| motion type | share of steps | model trans (mm) | zero trans (mm) | model / zero | "
          "model rot (deg) | zero rot (deg) | model / zero |",
          "|---|---|---|---|---|---|---|---|"]
    for typ in TYPES:
        r = np.array([x[2:] for x in rows if x[1] == typ], float)
        if not len(r):
            continue
        m = np.median(r, 0)
        res["by_type"][typ] = {"share": len(r) / len(rows), "n": len(r), "model_trans": m[0], "model_rot": m[1],
                               "zero_trans": m[2], "zero_rot": m[3]}
        md.append(f"| {typ} | {100 * len(r) / len(rows):.0f} % | {m[0]:.3f} | {m[2]:.3f} | {m[0] / m[2]:.2f} | "
                  f"{m[1]:.3f} | {m[3]:.3f} | {m[1] / m[3]:.2f} |")
    md += ["", "## Share of each motion type per held-out sweep", "",
           "| sweep | " + " | ".join(TYPES) + " |", "|---|" + "---|" * len(TYPES)]
    for sw in sweeps:
        s = [x for x in rows if x[0] == sw]
        shares = {t: sum(x[1] == t for x in s) / len(s) for t in TYPES}
        res["by_sweep"][sw] = shares
        md.append(f"| {sw} | " + " | ".join(f"{100 * shares[t]:.0f} %" for t in TYPES) + " |")
    (out / "motion_analysis.md").write_text("\n".join(md) + "\n")
    json.dump(res, open(out / "motion_analysis.json", "w"), indent=1)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    ty = [t for t in TYPES if t in res["by_type"]]
    x = np.arange(len(ty))
    for ax, (mk, zk, lab) in zip(axs, [("model_trans", "zero_trans", "translation error per step (mm)"),
                                       ("model_rot", "zero_rot", "rotation error per step (deg)")]):
        ax.bar(x - 0.2, [res["by_type"][t][zk] for t in ty], 0.38, color="#8f8e86", label="zero motion")
        ax.bar(x + 0.2, [res["by_type"][t][mk] for t in ty], 0.38, color="#2a78d6", label="model")
        ax.set_xticks(x)
        ax.set_xticklabels([f"{t}\n{100 * res['by_type'][t]['share']:.0f} % of steps" for t in ty], fontsize=8.5)
        ax.set_ylabel(f"median {lab}")
        ax.grid(True, axis="y", color="#e4e3dc")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    axs[0].legend(frameon=False)
    fig.suptitle(f"Where the odometry fails: error by motion type ({Path(args.arm).name}, {len(sweeps)} held-out sweeps)",
                 x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(out / "motion_analysis.png", dpi=140, facecolor="white")
    print(f"wrote {out}/motion_analysis.md, .png, .json")


if __name__ == "__main__":
    main()
