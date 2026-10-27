"""
Shape of the reconstruction: how much of the error at the US image a rigid motion explains, and
how well each pose source gets the motion between nearby US frames (what US images could correct).

Input: poses.py exports (<out>/poses/fold*_<run>_<source>.json, e.g. written by tools/volume_pages.py).
Points: the 5 points of anchoring.py spanning the US image. Per sweep and source:
  absolute  mean point error against Polaris, median over frames (as anchoring.py's US-image error)
  shape     the same after the best rigid fit of the whole sweep (all frames, all points) to Polaris:
            the error a rigid offset of the room frame cannot explain; this is what distorts the volume
  relative  for frame pairs k rows apart (same segment), the error of the relative pose at the points,
            in the US frame of the later image: in-plane (what US registration would see) and
            out-of-plane (along the plane normal; what speckle decorrelation measures)
Numbers are means over sweeps of the per-sweep medians. Rows are grouped by split (the folder that
holds poses/) and source.

  python tools/shape_error.py --json runs/volume3d-final/*/poses/*.json --out runs/shape-final.md
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

PX = np.array([[320, 240], [160, 120], [480, 120], [160, 400], [480, 400]], float)   # anchoring.py us_points


def kabsch(P, Q):
    """Rigid (R, t) minimising |R P + t - Q| for (N, 3) point sets."""
    mp, mq = P.mean(0), Q.mean(0)
    U, _, Vt = np.linalg.svd((P - mp).T @ (Q - mq))
    D = np.diag([1, 1, np.sign(np.linalg.det(Vt.T @ U.T))])
    R = Vt.T @ D @ U.T
    return R, mq - R @ mp


def sweep_metrics(doc, gaps):
    S = np.asarray(doc["S_us_px_to_mm"])
    P = S @ np.stack([PX[:, 0], PX[:, 1], np.zeros(5), np.ones(5)])           # (4, 5) US-plane mm
    fr = [f for f in doc["frames"] if f["us"] and np.all(np.isfinite(f["T_world_us_pred"]))
          and np.all(np.isfinite(f["T_world_us_gt"]))]
    if len(fr) < 2:
        return None
    Tp = np.array([f["T_world_us_pred"] for f in fr], float)
    Tg = np.array([f["T_world_us_gt"] for f in fr], float)
    Xp, Xg = (Tp @ P)[:, :3].transpose(0, 2, 1), (Tg @ P)[:, :3].transpose(0, 2, 1)   # (N, 5, 3)
    m = {"absolute": float(np.median(np.linalg.norm(Xp - Xg, axis=2).mean(1)))}
    R, t = kabsch(Xp.reshape(-1, 3), Xg.reshape(-1, 3))
    m["shape"] = float(np.median(np.linalg.norm(Xp @ R.T + t - Xg, axis=2).mean(1)))
    idx = {(f["segment"], f["row"]): n for n, f in enumerate(fr)}
    for k in gaps:
        pairs = [(n, idx[(s, r + k)]) for (s, r), n in idx.items() if (s, r + k) in idx]
        if not pairs:
            continue
        i, j = np.array(pairs).T
        rel = lambda T: np.linalg.inv(T[j]) @ T[i]                              # frame i in frame j
        E = (rel(Tp) @ P - rel(Tg) @ P)[:, :3]                                  # (M, 3, 5), mm in frame j
        m[f"in_{k}"] = float(np.median(np.linalg.norm(E[:, :2], axis=1).mean(1)))
        m[f"out_{k}"] = float(np.median(np.abs(E[:, 2]).mean(1)))
        m[f"true_out_{k}"] = float(np.median(np.abs((rel(Tg) @ P)[:, 2]).mean(1)))
    return m


def short(source):
    if "-scr-" in source or source.startswith("anchored-pgo-scr"):
        return "SCR anchors + odometry"
    if "pgo-classical" in source:
        return "classical anchors + odometry"
    if source.startswith("classical-vo"):
        return "classical odometry only"
    return source


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", nargs="+", required=True, help="poses.py exports")
    ap.add_argument("--gaps", type=int, nargs="+", default=[1, 8, 30], help="rows between the frames of a pair "
                    "(8 = one odometry step, 30 = 1 s)")
    ap.add_argument("--out", required=True, help="markdown file (a .json with every sweep is written next to it)")
    args = ap.parse_args()

    res = defaultdict(dict)                                 # (split, source) -> {run: metrics}
    for p in sorted(args.json):
        d = json.load(open(p))
        split = Path(p).resolve().parent.parent.name
        if d["run"] in res[(split, d["source"])]:
            continue                                        # the same sweep from another fold
        try:
            m = sweep_metrics(d, args.gaps)
        except Exception as e:                              # report and go on with the other files
            m = None
            print(f"{p}: {type(e).__name__}: {e}")
        if m is None:
            print(f"{split} {d['run']} {short(d['source'])}: skipped (no valid frames)")
            continue
        res[(split, d["source"])][d["run"]] = m
        print(f"{split} {d['run']} {short(d['source'])}: " + ", ".join(
            f"{k} {v:.2f}" for k, v in res[(split, d['source'])][d['run']].items()), flush=True)

    mean = lambda runs, k: np.mean([m[k] for m in runs.values() if k in m]) if any(k in m for m in runs.values()) else np.nan
    md = ["# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames", "",
          "Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit "
          "of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / "
          "**out-of-plane**, true out-of-plane motion in brackets.", "",
          "| split | source | sweeps | absolute | **shape** | " + " | ".join(f"k = {k}: in / **out** (true)" for k in args.gaps) + " |",
          "|---|---|---|---|---|" + "---|" * len(args.gaps)]
    for (split, src), runs in sorted(((k, r) for k, r in res.items() if r), key=lambda x: (x[0][0], short(x[0][1]))):
        md.append(f"| {split} | {short(src)} | {len(runs)} | {mean(runs, 'absolute'):.2f} | **{mean(runs, 'shape'):.2f}** | "
                  + " | ".join(f"{mean(runs, f'in_{k}'):.2f} / **{mean(runs, f'out_{k}'):.2f}** ({mean(runs, f'true_out_{k}'):.1f})"
                               for k in args.gaps) + " |")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md) + "\n")
    json.dump({"args": vars(args), "sweeps": {f"{s}|{src}": r for (s, src), r in res.items()}},
              open(out.with_suffix(".json"), "w"), indent=1)
    print("\n" + "\n".join(md[4:]) + f"\n-> {out}")


if __name__ == "__main__":
    main()
