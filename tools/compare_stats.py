"""
Per-sweep statistics: our system (no tracker) against ORB-SLAM3, paired by sweep.

For every split it reads our per-sweep US-image medians (`runs/<ours>/scr_track.json`, smoothed --window s) and
ORB-SLAM3's (`runs/slam-<split><tag>[-mode]/slam_eval.json`, smoothed 1 s by the evaluate commands), and reports,
per split and per session group (3XX, 4XX A-E, 5XX A-E with exam-view scans):

  mean of the per-sweep medians for each system; paired difference ORB-SLAM3 - ours with a 95 % bootstrap
  interval over sweeps; Wilcoxon signed-rank p (two-sided); sweeps where ours is lower.

Sweeps one system did not pose at all (NaN) are left out of the pair and counted. Splits whose folders do not
exist are skipped. With seed folders (`<ours>-seed1`, `-seed2`, from the seed commands in note.md) it also
reports our mean per seed.

  python tools/compare_stats.py --modes final online loc reloc --out runs/stats-orbslam.md
  python tools/compare_stats.py --tag -occ30 --modes loc reloc --out runs/stats-occ30.md   # occlusion test
"""

import argparse
import json
from pathlib import Path

import numpy as np

RUNS = Path(__file__).resolve().parent.parent / "runs"

# split -> our track folder (the headline runs of summary.md)
SPLITS = {
    "3XX": "repro/track-v2map-3XX",
    "4XXA": "track-v2map-4XXA", "4XXB": "track-v2map-4XXB", "4XXC": "track-v2map-4XXC",
    "4XXD": "track-v2map-4XXD", "4XXE": "track-v2map-4XXE",
    "5XXA-exam": "track-v2map-5XXA-exam", "5XXB-exam": "track-v2map-5XXB-exam", "5XXC-exam": "track-v2map-5XXC-exam",
    "5XXD-exam": "track-v2map-5XXD-exam", "5XXE-exam": "track-v2map-5XXE-exam",
    "5XXA-generic": "track-v2map-5XXA-generic", "5XXC-oldB": "track-v2map-5XXC-oldB", "5XXE-oldC": "track-v2map-5XXE-oldC",
}
GROUPS = {"3XX": ["3XX"], "4XX A-E": ["4XXA", "4XXB", "4XXC", "4XXD", "4XXE"],
          "5XX A-E (exam-view scans)": ["5XXA-exam", "5XXB-exam", "5XXC-exam", "5XXD-exam", "5XXE-exam"]}
GROUPS["all current maps"] = sum(GROUPS.values(), [])


def ours(folder, window):
    p = RUNS / folder / "scr_track.json"
    if not p.exists():
        return None
    d = json.load(open(p))["per_sweep"][f"smoothed {window:g} s"]
    return {sw: v["us_median"] for sw, v in d.items()}


def slam(split, tag, mode):
    p = RUNS / (f"slam-{split}{tag}" + ("" if mode == "final" else f"-{mode}")) / "slam_eval.json"
    if not p.exists():
        return None
    return {sw: v["us_median"] for sw, v in json.load(open(p))["sweeps"].items()}


def paired(a, b, rng):
    """a, b: {sweep: value}. Statistics of b - a over the sweeps both posed."""
    keys = [k for k in a if k in b and np.isfinite(a[k]) and np.isfinite(b[k])]
    x, y = np.array([a[k] for k in keys]), np.array([b[k] for k in keys])
    out = {"n": len(keys), "dropped": len(set(a) | set(b)) - len(keys), "a": x.mean() if len(x) else np.nan,
           "b": y.mean() if len(y) else np.nan, "wins_a": int((x < y).sum())}
    d = y - x
    if len(d) >= 2:
        boot = rng.choice(d, (10000, len(d))).mean(1)
        out["diff"], out["lo"], out["hi"] = d.mean(), *np.percentile(boot, [2.5, 97.5])
    else:
        out["diff"] = out["lo"] = out["hi"] = d.mean() if len(d) else np.nan
    try:
        from scipy.stats import wilcoxon
        out["p"] = float(wilcoxon(x, y).pvalue) if len(d) >= 5 and np.any(d != 0) else np.nan
    except ImportError:
        out["p"] = np.nan
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--modes", nargs="+", default=["final", "online", "loc", "reloc"],
                    help="ORB-SLAM3 runs: final = runs/slam-<split> (trajectory at shutdown), online / loc / reloc = "
                         "runs/slam-<split>-<mode>")
    ap.add_argument("--tag", default="", help="suffix of both folders, e.g. -occ30 for the occlusion test")
    ap.add_argument("--window", type=float, default=1.0, help="our smoothing window (s); ORB-SLAM3 is evaluated with 1 s")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    rng = np.random.default_rng(0)
    f2 = lambda v: "–" if not np.isfinite(v) else f"{v:.2f}"

    md = [f"# Our system against ORB-SLAM3, paired by sweep{f' ({args.tag})' if args.tag else ''}", "",
          f"US-image error (mm): median per sweep, mean over sweeps; ours smoothed {args.window:g} s, ORB-SLAM3 1 s. "
          "Difference = ORB-SLAM3 - ours (negative: ORB-SLAM3 better), 95 % bootstrap interval over sweeps; "
          "p = Wilcoxon signed-rank (two-sided, >= 5 sweeps); 'ours lower' = sweeps where our error is lower; "
          "'left out' = sweeps one system did not pose. `python tools/compare_stats.py` " +
          " ".join(f"--{k.replace('_', '-')} {' '.join(map(str, v)) if isinstance(v, list) else v}"
                   for k, v in vars(args).items() if k != "out" and v != ""), ""]
    for mode in args.modes:
        per = {}
        for split, folder in SPLITS.items():
            a, b = ours(folder + args.tag, args.window), slam(split, args.tag, mode)
            if a is not None and b is not None:
                per[split] = (a, b)
        if not per:
            continue
        md += [f"## ORB-SLAM3 {mode}", "", "| split | sweeps | ours | ORB-SLAM3 | difference [95 % CI] | p | ours lower | left out |",
               "|---|---|---|---|---|---|---|---|"]
        rows = [(s, *per[s]) for s in per]
        for g, splits in GROUPS.items():
            if all(s in per for s in splits) and len(splits) > 1:
                rows.append((f"**{g}**", {f"{s}/{k}": v for s in splits for k, v in per[s][0].items()},
                             {f"{s}/{k}": v for s in splits for k, v in per[s][1].items()}))
        for name, a, b in rows:
            r = paired(a, b, rng)
            p = "–" if not np.isfinite(r["p"]) else f"{r['p']:.3f}"
            md.append(f"| {name} | {r['n']} | {f2(r['a'])} | {f2(r['b'])} | {f2(r['diff'])} [{f2(r['lo'])}, {f2(r['hi'])}] | "
                      f"{p} | {r['wins_a']} / {r['n']} | {r['dropped']} |")
        md.append("")

    seeds = []
    for split, folder in SPLITS.items():
        vals = [ours(folder + sfx + args.tag, args.window) for sfx in ("", "-seed1", "-seed2")]
        if all(v is not None for v in vals):
            m = [np.nanmean(list(v.values())) for v in vals]
            seeds.append(f"| {split} | {' / '.join(f'{x:.2f}' for x in m)} | {np.mean(m):.2f} ± {np.std(m, ddof=1):.2f} |")
    if seeds:
        md += ["## Our seeds (0 / 1 / 2)", "", "| split | mean per seed | mean ± sd |", "|---|---|---|", *seeds, ""]

    Path(args.out).write_text("\n".join(md) + "\n")
    print("\n".join(md) + f"\n-> {args.out}")


if __name__ == "__main__":
    main()
