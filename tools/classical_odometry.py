"""
Classical RGB-D odometry baseline on exactly the steps the odometry network predicts (the
chains of an odometry arm on a test folder, e.g. frame gap 8): SIFT on both frames, frame k's
keypoints lifted to 3D with its depth, frame k+1's pose from PnP + RANSAC (as the classical
anchors, tools/anchor_classical.py). Where a step is not solved (< --min-inliers inliers,
e.g. the camera covered), the step is zero motion ("classical-vo") or the network's step
("classical-vo-hybrid").

Writes the steps in the network's cache format, so poses.py (US-image error) and
anchoring.py evaluate --odometry-source use them like the network's predictions:
    <arm>/preds/classical-vo-<test>_fold<k>.npz, classical-vo-hybrid-<test>_fold<k>.npz
and a per-sweep comparison with the network and zero motion in <out>/classical_vo.md:
per-step translation / rotation error, drift (final error / path length), maximum error;
each segment chained from its true start pose.

  python tools/classical_odometry.py --odometry runs/rpr-rgb-gap8-123XX-gru8 --test-root data/test_4XXA \\
      --out runs/rpr-rgb-gap8-123XX-gru8/test_4XXA
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import torch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from anchor_classical import pnp_pose, sift_features                  # noqa: E402
from anchoring import load_depth                                      # noqa: E402
from eval import load_val_set                                         # noqa: E402
from geometry import invert_se3, se3_exp, se3_log                     # noqa: E402
from trajectory import gt_chains                                      # noqa: E402


def step_errors(xi_pred, T_gt):
    """Per step: translation error (mm) and rotation error (deg) of T_k_k1."""
    Tp = se3_exp(xi_pred)
    Tg = invert_se3(T_gt[:-1]) @ T_gt[1:]
    et = np.linalg.norm(Tp[:, :3, 3] - Tg[:, :3, 3], axis=1)
    tr = np.einsum("nij,nij->n", Tp[:, :3, :3], Tg[:, :3, :3])
    return et, np.degrees(np.arccos(np.clip((tr - 1) / 2, -1, 1)))


def chain_errors(xi_pred, T_gt):
    """Chained from the true start: (final position error, max error, path length) in mm."""
    T = [T_gt[0]]
    for S in se3_exp(xi_pred):
        T.append(T[-1] @ S)
    e = np.linalg.norm(np.array(T)[:, :3, 3] - T_gt[:, :3, 3], axis=1)
    return float(e[-1]), float(e.max()), float(np.linalg.norm(np.diff(T_gt[:, :3, 3], axis=0), axis=1).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--odometry", required=True, help="odometry arm (its checkpoint defines the steps; its cache is compared)")
    ap.add_argument("--test-root", required=True)
    ap.add_argument("--test-runs", nargs="+", default=None)
    ap.add_argument("--out", required=True, help="folder for classical_vo.md / .json")
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--features", type=int, default=4000)
    ap.add_argument("--ratio", type=float, default=0.8)
    ap.add_argument("--ransac-px", type=float, default=4.0)
    ap.add_argument("--min-inliers", type=int, default=20)
    args = ap.parse_args()
    arm, out = Path(args.odometry), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    test = Path(args.test_root).name

    ock = torch.load(arm / f"fold{args.fold}" / "best.pt", map_location="cpu", weights_only=False)
    ds, _, runs = load_val_set(ock, args.test_root, args.test_runs)
    chains = gt_chains(ds)
    net_cache = arm / "preds" / f"fold{args.fold}_{test}.npz"
    net = None                                       # the network's steps, for the comparison and the hybrid
    if net_cache.exists():
        z = np.load(net_cache, allow_pickle=True)
        net = {(str(r), int(s)): v for (r, s), v in zip(z["keys"], z["values"])}
    else:
        print(f"{net_cache} missing (run eval.py on {arm} with --test-root to compare): classical only")
    sift = cv2.SIFT_create(nfeatures=args.features)
    dmin, dmax = ds.cfg.min_depth, ds.cfg.max_depth

    def feats(run, row):
        g = cv2.imread(str(Path(args.test_root) / run / ds.runs[run]["df"]["rgb"].iloc[row]), cv2.IMREAD_GRAYSCALE)
        return sift_features(g, load_depth(run, row, ds.runs, args.test_root), sift)

    vo, hyb, rows = {}, {}, {}
    for (run, sid), c in chains.items():
        K = np.array(ds.runs[run]["K"], float)
        fr, T_gt = c["frames"], c["T_gt"]
        prev = feats(run, int(fr[0]))
        xs, solved = [], []
        for k in range(1, len(fr)):
            cur = feats(run, int(fr[k]))
            T, _, _ = pnp_pose(prev, cur, K, args.ratio, args.ransac_px, args.min_inliers, dmin, dmax)
            xs.append(se3_log(T[None])[0] if T is not None else np.zeros(6))
            solved.append(T is not None)
            prev = cur
        xs, solved = np.array(xs), np.array(solved)
        vo[(run, sid)] = xs
        if net is not None:
            hyb[(run, sid)] = np.where(solved[:, None], xs, net[(run, sid)])
        r = rows.setdefault(run, {"steps": 0, "solved": 0, "et": {}, "er": {}, "final": {}, "max": {}, "path": 0.0})
        r["steps"] += len(xs)
        r["solved"] += int(solved.sum())
        r["path"] += chain_errors(xs, T_gt)[2]
        compared = [("zero", np.zeros_like(xs)), ("classical", xs)]
        if net is not None:
            compared += [("network", net[(run, sid)]), ("hybrid", hyb[(run, sid)])]
        for name, x in compared:
            et, er = step_errors(x, T_gt)
            f, m, _ = chain_errors(x, T_gt)
            r["et"].setdefault(name, []).extend(et.tolist())
            r["er"].setdefault(name, []).extend(er.tolist())
            r["final"].setdefault(name, []).append(f)
            r["max"].setdefault(name, []).append(m)
        print(f"  {run} segment {sid}: {len(xs)} steps, {100 * solved.mean():.0f} % solved", flush=True)

    for name, d in (("classical-vo", vo), ("classical-vo-hybrid", hyb)) if net is not None else (("classical-vo", vo),):
        keys = list(d)
        values = np.empty(len(keys), dtype=object)
        values[:] = [d[k] for k in keys]
        np.savez(arm / "preds" / f"{name}-{test}_fold{args.fold}.npz", keys=np.array(keys, dtype=object), values=values)

    methods = ("zero", "network", "classical", "hybrid") if net is not None else ("zero", "classical")
    table = {}
    for run, r in rows.items():
        table[run] = {"steps": r["steps"], "solved_pct": 100 * r["solved"] / max(r["steps"], 1)}
        for m in methods:
            table[run][m] = {"step_t_mm": float(np.median(r["et"][m])), "step_r_deg": float(np.median(r["er"][m])),
                             "drift_pct": 100 * float(np.sum(r["final"][m]) / max(r["path"], 1e-6)),
                             "max_mm": float(np.max(r["max"][m]))}
    json.dump({"settings": vars(args), "per_sweep": table}, open(out / "classical_vo.json", "w"), indent=1)
    md = [f"# Classical RGB-D odometry (SIFT + PnP-RANSAC) vs {arm.name} on {test}", "",
          "Same steps as the network (its frame gap); per step: median translation (mm) / rotation (deg) error; "
          "drift: final error / path length; max: largest error along the sweep (chained from the true start). "
          "Hybrid: classical where solved, else the network.", "",
          "| sweep | steps solved | " + " | ".join(f"{m}: step mm / deg, drift %, max mm" for m in methods) + " |",
          "|---|---|" + "---|" * len(methods)]
    for run, t in table.items():
        md.append(f"| {run} | {t['solved_pct']:.0f} % | " + " | ".join(
            f"{t[m]['step_t_mm']:.2f} / {t[m]['step_r_deg']:.2f}, {t[m]['drift_pct']:.1f}, {t[m]['max_mm']:.0f}" for m in methods) + " |")
    mean = lambda m, k: np.mean([t[m][k] for t in table.values()])
    md.append(f"| **mean** | {np.mean([t['solved_pct'] for t in table.values()]):.0f} % | " + " | ".join(
        f"{mean(m, 'step_t_mm'):.2f} / {mean(m, 'step_r_deg'):.2f}, {mean(m, 'drift_pct'):.1f}, {mean(m, 'max_mm'):.0f}" for m in methods) + " |")
    md += ["", f"US-image error: `python poses.py --ckpts {arm}/fold{args.fold}/best.pt --test-root {args.test_root} "
               f"--out {out} --no-plot --source classical-vo-{test}` (or classical-vo-hybrid-{test})."]
    (out / "classical_vo.md").write_text("\n".join(md) + "\n")
    print("\n" + "\n".join(md[4:]) + f"\n-> {out / 'classical_vo.md'}")


if __name__ == "__main__":
    main()
