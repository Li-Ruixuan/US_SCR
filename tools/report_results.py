"""
One results table for one evaluation set (e.g. the validation sweeps, or the 3XX test sweeps):
per sweep, then the mean with a 95 % bootstrap interval over sweeps (sweeps are the
independent unit; with 2-5 sweeps the interval is wide, and that is the point). CPU only;
reads what eval.py, poses.py and anchoring.py evaluate already wrote.

Columns: per-pair error vs zero motion (eval.py), drift % of path length, median error at
the US image unanchored and with the pose graph (anchoring.py evaluate), anchor error, and
mean US pixel error / Dice from compounding (poses.py) for odometry, zero motion, anchored.

  python tools/report_results.py --name "2XX validation" --eval runs/rpr-rgb-gap4/eval.json \
      --compound runs/rpr-rgb-gap4/compound --anchors runs/anchoring/anchor_eval_anchor-rgbd-odometry.json
  python tools/report_results.py --name "3XX test, own map" --eval runs/rpr-rgb-gap4/test_3XX/eval.json \
      --compound runs/rpr-rgb-gap4/test_3XX/compound runs/rpr-rgb-gap4/test_3XX_ownmap/compound \
      --anchors "runs/anchoring/anchor_eval_anchor-rgbd-odometry-train_3XX-map-room-301+room-302.json"
"""

import argparse
import json
from pathlib import Path

import numpy as np

COLS = [  # key, header, format
    ("pair_t", "pair transl. vs zero", "+.0f"),
    ("pair_r", "pair rot. vs zero", "+.0f"),
    ("drift", "drift % of path", ".1f"),
    ("us_none", "US median, unanchored (mm)", ".1f"),
    ("us_pgo", "US median, pose graph (mm)", ".1f"),
    ("anchor", "anchor error (mm)", ".1f"),
    ("pix_zero", "pixel error, zero (mm)", ".1f"),
    ("pix_model", "pixel error, odometry (mm)", ".1f"),
    ("pix_anch", "pixel error, anchored (mm)", ".1f"),
    ("dice_anch", "Dice, anchored", ".2f"),
]


def odometry_rows(path):
    rows = {}
    for x in json.load(open(path)):
        per = x.get("per_run") or {x["val_runs"][0]: x}
        for run, v in per.items():
            m, z = v["model"], v["zero"]
            rows[run] = {"pair_t": 100 * (m["pair"]["trans_mm_median"] / z["pair"]["trans_mm_median"] - 1),
                         "pair_r": 100 * (m["pair"]["rot_deg_median"] / z["pair"]["rot_deg_median"] - 1),
                         "drift": m["summary"]["drift_pct_aggregate"]}
    return rows


def compound_rows(dirs):
    rows = {}
    for d in dirs:
        for f in sorted(Path(d).glob("summary_*.json")):
            src = f.stem[len("summary_"):]
            key = ("zero" if src == "zero" else "model" if src == "model"
                   else "anch" if src.startswith("anchored-pgo") else None)
            if key is None:
                continue
            for run, v in json.load(open(f))["per_sweep"].items():
                rows.setdefault(run, {})[f"pix_{key}"] = v["pixel_error_mm"]
                if key == "anch":
                    rows[run]["dice_anch"] = v["dice"]
    return rows


def anchor_rows(path):
    return {run: {"us_none": v["none"]["us_median"], "us_pgo": v.get("pgo", {}).get("us_median", np.nan),
                  "anchor": v["anchors"]["err_mm_median"]}
            for run, v in json.load(open(path))["per_sweep"].items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", required=True, help="label of the evaluation set")
    ap.add_argument("--eval", required=True, help="eval.json of the odometry arm for this set")
    ap.add_argument("--compound", nargs="*", default=[], help="compound/ folders of poses.py for this set")
    ap.add_argument("--anchors", default=None, help="anchor_eval_*.json of anchoring.py evaluate for this set")
    ap.add_argument("--out", default=None, help="also write the table as markdown")
    args = ap.parse_args()

    rows = odometry_rows(args.eval)
    for extra in (compound_rows(args.compound), anchor_rows(args.anchors) if args.anchors else {}):
        for run, v in extra.items():
            rows.setdefault(run, {}).update(v)
    cols = [c for c in COLS if any(c[0] in r for r in rows.values())]
    runs = sorted(rows)

    rng = np.random.default_rng(0)
    md = [f"### {args.name} ({len(runs)} sweeps)", "",
          "| sweep | " + " | ".join(c[1] for c in cols) + " |", "|---|" + "---|" * len(cols)]
    for run in runs:
        md.append(f"| {run} | " + " | ".join(
            (f"{rows[run][k]:{f}}" + (" %" if k.startswith("pair") else "")) if k in rows[run] else "–"
            for k, _, f in cols) + " |")
    mean, ci = [], []
    for k, _, f in cols:
        x = np.array([rows[r].get(k, np.nan) for r in runs], float)
        x = x[np.isfinite(x)]
        if not len(x):
            mean.append("–"); ci.append("–")
            continue
        b = x[rng.integers(0, len(x), (5000, len(x)))].mean(1)
        mean.append(f"**{x.mean():{f}}**")
        ci.append(f"[{np.percentile(b, 2.5):{f}}, {np.percentile(b, 97.5):{f}}]")
    md.append("| **mean** | " + " | ".join(mean) + " |")
    md.append("| 95 % CI | " + " | ".join(ci) + " |")
    md += ["", "Pair columns: change of the median per-pair error against zero motion (negative = better). "
           "US median: median distance at points on the US image (mm). Pixel error: mean over the US image "
           "after compounding. CI: bootstrap over sweeps."]
    text = "\n".join(md)
    print(text)
    if args.out:
        Path(args.out).write_text(text + "\n")
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
