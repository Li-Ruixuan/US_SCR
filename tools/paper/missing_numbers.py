"""
Missing numbers of the TBME paper (spec: missing_numbers.md; plan: rerun_plan.md, Tier 0, steps 0c + 0d).

Read only: per-sweep US-image errors from runs/<track>/scr_track.json (all windows stored) and ORB-SLAM3's
slam_eval.json (one window per file). Nothing is trained, mapped or re-scored here.

Every item first reproduces numbers that are already in the paper, at the window the paper used for them
(F1 / F2 / seeds: 2 s; phantom: 1 s; ORB-SLAM3 comparison: ours 1 s against runs/slam-* at 1 s). Only then
is the item reported at --window, with ORB-SLAM3 from --slam-dir. A failed check marks the item
CHECK FAILED and the item is not reported; the script exits with status 1 if any check failed.

  python tools/paper/missing_numbers.py --window 2 --slam-dir runs/paper_final --out runs/paper_final/numbers

Outputs in --out: missing_numbers.json, missing_numbers_report.md, persweep_orbslam.csv, persweep_orbslam.tex.
Paper names only in the 'latex' fields and in the .tex table; repo folders appear only in 'source_files'.
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
from scipy.stats import wilcoxon

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "runs"
sys.path.insert(0, str(REPO / "tools"))
import compare_stats as cs  # noqa: E402  (paired(), SPLITS, GROUPS: same statistics and bootstrap order)

# paper name -> (compare_stats split, our track folder under runs/)
SETS = {
    "F1-test":  ("3XX", "repro/track-v2map-3XX"),
    "F2-new":   ("4XXA", "track-v2map-4XXA"),
    "F2-small": ("4XXB", "track-v2map-4XXB"),
    "F2-large": ("4XXC", "track-v2map-4XXC"),
    "F2-subj2": ("4XXD", "track-v2map-4XXD"),
    "F2-arm":   ("4XXE", "track-v2map-4XXE"),
    "P-ref":    ("5XXA-exam", "track-v2map-5XXA-exam"),
    "P-rearr1": ("5XXB-exam", "track-v2map-5XXB-exam"),
    "P-rearr2": ("5XXC-exam", "track-v2map-5XXC-exam"),
    "P-people": ("5XXD-exam", "track-v2map-5XXD-exam"),
    "P-empty":  ("5XXE-exam", "track-v2map-5XXE-exam"),
}
F2 = ["F2-new", "F2-small", "F2-large", "F2-subj2", "F2-arm"]
PH = ["P-ref", "P-rearr1", "P-rearr2", "P-people", "P-empty"]
GENERIC = "track-v2map-5XXA-generic"
SELF_SEEDS = ["repro/track-v2map-3XX", "repro/track-v2map-3XX-seed1", "repro/track-v2map-3XX-seed2"]
ORACLE_SEEDS = ["track-3XX", "track-3XX-seed1", "track-3XX-seed2"]
MODES = ["final", "online", "loc", "loc-r2", "loc-r3", "reloc"]   # order of runs/stats-orbslam.md (bootstrap order)
MODE_NAME = {"final": "full SLAM", "online": "full SLAM, online poses", "loc": "localisation only",
             "loc-r2": "localisation only, run 2", "loc-r3": "localisation only, run 3",
             "reloc": "each frame relocalised"}
ALL63 = "all current maps"

# values already in the paper, at the window the paper used (checks)
PAPER = {
    "F1-test": 2.34, "F1-test_sd": 0.47, "F2_sets": 7.92, "F2_sets_sd": 2.56,           # 2 s
    "phantom": [2.28, 4.43, 3.11, 2.24, 5.85], "generic": 13.57,                          # 1 s
    "self_seeds": [2.34, 2.22, 2.25], "self_seed_mean": 2.27, "oracle_seeds": [1.85, 1.95, 2.12],  # 2 s
}
# runs/stats-orbslam.md, row 'all current maps' (ours 1 s vs ORB-SLAM3 1 s; diff = ORB-SLAM3 - ours)
STATS_1S = {"final": (63, 5.14, 2.85, -2.30, -3.03, -1.62, 12), "online": (63, 5.14, 3.12, -2.02, -2.66, -1.42, 12),
            "loc": (63, 5.14, 4.46, -0.68, -2.38, 2.13, 14), "loc-r2": (63, 5.14, 3.10, -2.05, -2.67, -1.43, 12),
            "loc-r3": (63, 5.14, 3.55, -1.59, -2.48, -0.52, 14), "reloc": (63, 5.14, 3.19, -1.96, -2.61, -1.30, 11)}
ORB_LOWER_1S = {"reloc": 52, "final": 51, "loc": 49}   # paper / missing_numbers.md M7


# ---------------------------------------------------------------- loading

def key(window):
    return f"smoothed {window:g} s"


def track(folder, window, field="us_median"):
    """{sweep: value} of our system; None if the folder is missing."""
    p = RUNS / folder / "scr_track.json"
    if not p.exists():
        return None
    return {sw: v[field] for sw, v in json.load(open(p))["per_sweep"][key(window)].items()}


def slam_file(slam_dir, split, mode):
    return Path(slam_dir) / (f"slam-{split}" + ("" if mode == "final" else f"-{mode}")) / "slam_eval.json"


def slam(slam_dir, split, mode, field="us_median"):
    p = slam_file(slam_dir, split, mode)
    if not p.exists():
        return None
    return {sw: v[field] for sw, v in json.load(open(p))["sweeps"].items()}


def slam_window(slam_dir, split, mode):
    p = slam_file(slam_dir, split, mode)
    return json.load(open(p))["args"]["smooth"] if p.exists() else None


def vals(d):
    return np.array([d[k] for k in sorted(d)], float)


def msd(x):
    x = np.asarray(x, float)
    return float(np.mean(x)), (float(np.std(x, ddof=1)) if len(x) > 1 else float("nan"))


def close(got, exp, dec=2):
    return got is not None and np.isfinite(got) and abs(got - exp) <= 0.5 * 10 ** -dec + 1e-9


def wil(x, y):
    """Two-sided Wilcoxon signed-rank: exact for n <= 25, else scipy's default."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 5 or not np.any(x != y):
        return float("nan")
    return float(wilcoxon(x, y, method="exact").pvalue if len(x) <= 25 else wilcoxon(x, y).pvalue)


def rel(p):
    return str(Path(p).resolve().relative_to(REPO)) if str(Path(p).resolve()).startswith(str(REPO)) else str(p)


def entry(id_, values, n, exp, got, ok, sources, latex, note=""):
    return {"id": id_, "values": values, "n": n, "check_expected": exp, "check_got": got,
            "check_ok": ok, "source_files": sources, "latex": latex, "note": note}


def failed(id_, exp, got, sources, note=""):
    return entry(id_, "CHECK FAILED", None, exp, got, False, sources, None, note)


# ---------------------------------------------------------------- items

def m1():
    files = [f"runs/{SETS[s][1]}/scr_track.json" for s in PH]
    n = {s: len(track(SETS[s][1], 1.0)) for s in PH}
    got = {"P-ref": n["P-ref"], "P-rearr1": n["P-rearr1"], "P-rearr2": n["P-rearr2"], "total": sum(n.values())}
    exp = {"P-ref": 8, "P-rearr1": 8, "P-rearr2": 8, "total": 32}
    if got != exp:
        return failed("M1", exp, got, files)
    return entry("M1", n, sum(n.values()), exp, got, True, files,
                 {"P-people": f"{n['P-people']}", "P-empty": f"{n['P-empty']}"})


def per_set(window):
    return {s: vals(track(SETS[s][1], window)) for s in SETS}


def m2(window):
    files = [f"runs/{SETS[s][1]}/scr_track.json" for s in SETS]
    p2, p1 = per_set(2.0), per_set(1.0)
    f1m, f1s = msd(p2["F1-test"])
    f2m, f2s = msd([p2[s].mean() for s in F2])
    ph1 = [p1[s].mean() for s in PH]
    got = {"F1-test (2 s)": [round(f1m, 2), round(f1s, 2)], "F2 over 5 sets (2 s)": [round(f2m, 2), round(f2s, 2)],
           "phantom sets (1 s)": [round(v, 2) for v in ph1]}
    exp = {"F1-test (2 s)": [PAPER["F1-test"], PAPER["F1-test_sd"]], "F2 over 5 sets (2 s)": [PAPER["F2_sets"], PAPER["F2_sets_sd"]],
           "phantom sets (1 s)": PAPER["phantom"]}
    ok = (close(f1m, PAPER["F1-test"]) and close(f1s, PAPER["F1-test_sd"]) and close(f2m, PAPER["F2_sets"])
          and close(f2s, PAPER["F2_sets_sd"]) and all(close(g, e) for g, e in zip(ph1, PAPER["phantom"])))
    if not ok:
        return failed("M2", exp, got, files)

    p = per_set(window)
    out = {s: dict(zip(["mean", "sd"], msd(p[s])), n=len(p[s])) for s in SETS}
    f2sets, phsets = msd([p[s].mean() for s in F2]), msd([p[s].mean() for s in PH])
    f2sw, phsw = msd(np.concatenate([p[s] for s in F2])), msd(np.concatenate([p[s] for s in PH]))
    out["F2, over 5 sets"] = {"mean": f2sets[0], "sd": f2sets[1], "n": 5}
    out["F2, over sweeps"] = {"mean": f2sw[0], "sd": f2sw[1], "n": sum(len(p[s]) for s in F2)}
    out["phantom, over 5 sets"] = {"mean": phsets[0], "sd": phsets[1], "n": 5}
    out["phantom, over sweeps"] = {"mean": phsw[0], "sd": phsw[1], "n": sum(len(p[s]) for s in PH)}
    latex = {k: f"{v['mean']:.2f}\\pm{v['sd']:.2f}" for k, v in out.items()}
    return entry("M2", out, {k: v["n"] for k, v in out.items()}, exp, got, True, files, latex,
                 f"window {window:g} s; SD ddof=1. D2: the paper's F2 / phantom headline is the mean over the 5 sets.")


def m3(window):
    files = [f"runs/{SETS['P-ref'][1]}/scr_track.json", f"runs/{GENERIC}/scr_track.json"]
    e1, g1 = track(SETS["P-ref"][1], 1.0), track(GENERIC, 1.0)
    got = [round(vals(e1).mean(), 2), round(vals(g1).mean(), 2)]
    exp = [PAPER["phantom"][0], PAPER["generic"]]
    if not (close(got[0], exp[0]) and close(got[1], exp[1])):
        return failed("M3", exp, got, files)
    e, g = track(SETS["P-ref"][1], window), track(GENERIC, window)
    ks = sorted(set(e) & set(g))
    x, y = np.array([e[k] for k in ks]), np.array([g[k] for k in ks])
    p = float(wilcoxon(x, y, method="exact").pvalue)
    v = {"exam_mean": float(x.mean()), "generic_mean": float(y.mean()), "p_exact": p, "exam_lower": int((x < y).sum())}
    return entry("M3", v, len(ks), exp, got, True, files,
                 f"p={p:.4f}", f"window {window:g} s; paired by sweep; exact two-sided Wilcoxon (min. p for n=8 is 0.0078)")


def m4():
    """Lookup: the near / far table (runs/coverage_error.md, PnP, oracle map). Re-evaluation is Tier 1 (B1)."""
    f = RUNS / "coverage_error.md"
    txt = f.read_text()
    blocks = re.split(r"^### ", txt, flags=re.M)[1:]
    rows = {}
    for b in blocks:
        name = b.splitlines()[0].strip()
        c = re.search(r"\*\*covered[^|]*\*\* \| (\d+) \([^)]*\) \| ([\d.–-]+)", b)
        u = re.search(r"\*\*not covered\*\* \| (\d+) \([^)]*\) \| ([\d.–-]+)", b)
        tofl = lambda s: float(s) if re.match(r"^[\d.]+$", s) else None
        rows[name] = {"near_frames": int(c.group(1)) if c else None, "near_median": tofl(c.group(2)) if c else None,
                      "far_frames": int(u.group(1)) if u else None, "far_median": tofl(u.group(2)) if u else None}
    pooled = rows.get("all files pooled", {})
    got = [pooled.get("near_median"), pooled.get("far_median")]
    exp = [4.1, 13.4]
    if not (close(got[0], 4.1, 1) and close(got[1], 13.4, 1)):
        return failed("M4", exp, got, ["runs/coverage_error.md"])
    return entry("M4", rows, pooled.get("near_frames", 0) + pooled.get("far_frames", 0), exp, got, True,
                 ["runs/coverage_error.md"], None,
                 "lookup of the existing PnP analysis (v1 networks, oracle map, 10 evaluations incl. cross-block and "
                 "outdated-map cases); per-set rows use repo names. D4 (Kabsch) needs Tier 1 block B1.")


def m5():
    return entry("M5", {
        "6.3 mm run": "fixed recipe, 360x640, PnP, 30 epochs (s1-2XX)",
        "7.3 mm run": "same, 720x1280 input (s3-full-2XX)",
        "differences from final 3.4 mm": "epochs 30 vs 120; PnP vs Kabsch",
        "footnote a": "15.8 mm: 15 epochs, PnP (first recipe, fp32 head off); 5.1 mm: 120 epochs, PnP"},
        None, None, None, None,
        ["git show 27adf4c3~1:runs/s1-2XX/config.json", "git show 27adf4c3~1:runs/s3-full-2XX/config.json",
         "runs/s1-base-2XX/config.json", "runs/s1-e120-2XX/config.json", "summary.md (4.1)"],
        None, "lookup done by hand on 2026-11-20 (missing_numbers.md, 5.1); not recomputed")


def m6(window):
    files = [f"runs/{f}/scr_track.json" for f in SELF_SEEDS + ORACLE_SEEDS]
    s2 = [vals(track(f, 2.0)).mean() for f in SELF_SEEDS]
    o2 = [vals(track(f, 2.0)).mean() for f in ORACLE_SEEDS]
    got = {"self": [round(v, 2) for v in s2], "self_mean": round(float(np.mean(s2)), 2), "oracle": [round(v, 2) for v in o2]}
    exp = {"self": PAPER["self_seeds"], "self_mean": PAPER["self_seed_mean"], "oracle": PAPER["oracle_seeds"]}
    ok = (all(close(g, e) for g, e in zip(s2, PAPER["self_seeds"])) and close(float(np.mean(s2)), PAPER["self_seed_mean"])
          and all(close(g, e) for g, e in zip(o2, PAPER["oracle_seeds"])))
    if not ok:
        return failed("M6", exp, got, files)
    s = [float(vals(track(f, window)).mean()) for f in SELF_SEEDS]
    o = [float(vals(track(f, window)).mean()) for f in ORACLE_SEEDS]
    d = [a - b for a, b in zip(s, o)]
    v = {"self": s, "oracle": o, "paired_diff": d, "self_mean": float(np.mean(s)), "oracle_mean": float(np.mean(o)),
         "mean_gap": float(np.mean(s) - np.mean(o))}
    return entry("M6", v, 3, exp, got, True, files,
                 {"seed-mean gap": f"{v['mean_gap']:.2f}", "seed-0 gap": f"{d[0]:.2f}",
                  "paired range": f"{min(d):.2f}--{max(d):.2f}"},
                 f"window {window:g} s; pairing by seed number (self-mapped: mapping + training seed; oracle: training seed)")


def orbslam_stats(window, slam_dir):
    """Exactly the loop of compare_stats.main(): one rng, modes and rows in the same order -> same bootstrap draws."""
    rng = np.random.default_rng(0)
    res, files = {}, []
    for mode in MODES:
        per = {}
        for split, folder in cs.SPLITS.items():
            a, b = track(folder, window), slam(slam_dir, split, mode)
            if a is not None and b is not None:
                per[split] = (a, b)
                files.append(rel(slam_file(slam_dir, split, mode)))
        if not per:
            continue
        rows = [(s, *per[s]) for s in per]
        for g, splits in cs.GROUPS.items():
            if all(s in per for s in splits) and len(splits) > 1:
                rows.append((g, {f"{s}/{k}": v for s in splits for k, v in per[s][0].items()},
                             {f"{s}/{k}": v for s in splits for k, v in per[s][1].items()}))
        res[mode] = {}
        for name, a, b in rows:
            r = cs.paired(a, b, rng)
            ks = [k for k in a if k in b and np.isfinite(a[k]) and np.isfinite(b[k])]
            x, y = np.array([a[k] for k in ks]), np.array([b[k] for k in ks])
            r["orb_lower"] = int((y < x).sum())
            r["p_spec"] = wil(x, y)          # exact for n <= 25 (spec); r["p"] is compare_stats' default method
            res[mode][name] = r
    return res, sorted(set(files))


def m7(window, slam_dir):
    old, f1 = orbslam_stats(1.0, RUNS)
    got, ok = {}, True
    for mode, (n, a, b, d, lo, hi, wins) in STATS_1S.items():
        r = old.get(mode, {}).get(ALL63)
        if r is None:
            got[mode] = None
            ok = False
            continue
        got[mode] = [r["n"], round(r["a"], 2), round(r["b"], 2), round(r["diff"], 2), round(r["lo"], 2), round(r["hi"], 2), r["wins_a"]]
        ok &= (r["n"] == n and r["wins_a"] == wins and all(close(g, e) for g, e in
                                                           zip([r["a"], r["b"], r["diff"], r["lo"], r["hi"]], [a, b, d, lo, hi])))
    for mode, k in ORB_LOWER_1S.items():
        ok &= old.get(mode, {}).get(ALL63, {}).get("orb_lower") == k
    exp = {m: list(v) for m, v in STATS_1S.items()}
    if not ok:
        return failed("M7", exp, got, f1, "self-check at 1 s against runs/stats-orbslam.md failed"), None

    wins = {slam_window(slam_dir, s, m) for m in MODES for s in cs.SPLITS if slam_window(slam_dir, s, m) is not None}
    if wins != {window}:
        return failed("M7", {"ORB-SLAM3 window": window}, {"ORB-SLAM3 window": sorted(wins)}, [str(slam_dir)],
                      "the ORB-SLAM3 files in --slam-dir are not at --window"), None
    new, f2 = orbslam_stats(window, slam_dir)
    v, latex = {}, {}
    for mode, rows in new.items():
        for g in ["4XX A-E", "5XX A-E (exam-view scans)", ALL63]:
            r = rows.get(g)
            if r is None:
                continue
            gname = {"4XX A-E": "F2", "5XX A-E (exam-view scans)": "phantom (exam-view scans)", ALL63: "all 63 test sweeps"}[g]
            # proposed - ORB-SLAM3 = -(ORB-SLAM3 - ours)
            v[f"{MODE_NAME[mode]} | {gname}"] = {
                "n": r["n"], "ours": r["a"], "orbslam": r["b"], "diff": -r["diff"], "ci": [-r["hi"], -r["lo"]],
                "p": r["p"], "p_spec": r["p_spec"], "orb_lower": r["orb_lower"], "left_out": r["dropped"]}
            if g == ALL63:
                ptxt = "p<0.001" if r["p"] < 0.001 else f"p={r['p']:.3f}"
                latex[MODE_NAME[mode]] = (f"lower on {r['orb_lower']} of {r['n']} sweeps, on average by {-r['diff']:.2f}\\,mm "
                                          f"(95\\,\\% bootstrap interval {-r['hi']:.2f}--{-r['lo']:.2f}\\,mm; Wilcoxon ${ptxt}$)")
    reps = [new[m][ALL63]["b"] for m in ["loc", "loc-r2", "loc-r3"] if m in new and ALL63 in new[m]]
    if len(reps) == 3:
        v["localisation only, 3 runs | all 63 test sweeps"] = {"orbslam_means": reps, "spread": [min(reps), max(reps)]}
        latex["localisation only, run-to-run"] = f"{min(reps):.2f}--{max(reps):.2f}\\,mm"
    return entry("M7", v, 63, exp, got, True, sorted(set(f1 + f2)), latex,
                 f"ours {window:g} s vs ORB-SLAM3 {window:g} s ({rel(slam_dir)}); diff = proposed - ORB-SLAM3; bootstrap "
                 "10 000 x default_rng(0) in the order of compare_stats.py; 'p' = scipy default (as compare_stats), "
                 "'p_spec' = exact for n <= 25"), new


def m8(window, slam_dir, out):
    rows, files = [], []
    for name, (split, folder) in SETS.items():
        e = track(folder, window)
        c = track(folder, window, "coverage_pct")
        files.append(f"runs/{folder}/scr_track.json")
        orb = {}
        for m in ["final", "loc", "reloc"]:
            orb[m] = (slam(slam_dir, split, m) or {}, slam(slam_dir, split, m, "coverage_pct") or {})
            files.append(rel(slam_file(slam_dir, split, m)))
        for i, sw in enumerate(sorted(e), 1):
            r = {"set": name, "sweep": i, "ours": e[sw], "ours_posed": c[sw]}
            for m in orb:
                r[m] = orb[m][0].get(sw, float("nan"))
                r[f"{m}_posed"] = orb[m][1].get(sw, float("nan"))
            rows.append(r)
    if len(rows) != 63:
        return failed("M8", 63, len(rows), files)

    # check: the per-set column means equal the per-set means of M2 (ours) and of slam_eval.json (ORB-SLAM3)
    bad = []
    for name, (split, folder) in SETS.items():
        rs = [r for r in rows if r["set"] == name]
        if not close(np.mean([r["ours"] for r in rs]), vals(track(folder, window)).mean(), 4):
            bad.append(f"{name} ours")
        for m in ["final", "loc", "reloc"]:
            s = slam(slam_dir, split, m)
            if s and not close(np.nanmean([r[m] for r in rs]), np.nanmean(list(s.values())), 4):
                bad.append(f"{name} {m}")
    if bad:
        return failed("M8", "column means = per-set means", bad, files)

    cols = ["set", "sweep", "ours", "ours_posed", "final", "final_posed", "loc", "loc_posed", "reloc", "reloc_posed"]
    with open(out / "persweep_orbslam.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({k: (f"{r[k]:.4f}" if isinstance(r[k], float) else r[k]) for k in cols})
    f2 = lambda x: "--" if not np.isfinite(x) else f"{x:.2f}"
    p0 = lambda x: "--" if not np.isfinite(x) else f"{x:.0f}"
    tex = ["% generated by tools/paper/missing_numbers.py; US-image error (mm), median per sweep, "
           f"offline smoothing {window:g} s; posed share in %",
           "\\begin{longtable}{llrrrrrrrr}",
           "\\toprule",
           " & & \\multicolumn{2}{c}{Proposed} & \\multicolumn{2}{c}{Full SLAM} & \\multicolumn{2}{c}{Localisation only}"
           " & \\multicolumn{2}{c}{Each frame relocalised}\\\\",
           "Set & Sweep & mm & \\% & mm & \\% & mm & \\% & mm & \\%\\\\",
           "\\midrule", "\\endhead", "\\bottomrule", "\\endfoot"]
    prev = None
    for r in rows:
        if prev is not None and r["set"] != prev:
            tex.append("\\midrule")
        prev = r["set"]
        tex.append(f"{r['set']} & {r['sweep']} & {f2(r['ours'])} & {p0(r['ours_posed'])} & {f2(r['final'])} & "
                   f"{p0(r['final_posed'])} & {f2(r['loc'])} & {p0(r['loc_posed'])} & {f2(r['reloc'])} & {p0(r['reloc_posed'])}\\\\")
    tex.append("\\end{longtable}")
    (out / "persweep_orbslam.tex").write_text("\n".join(tex) + "\n")
    return entry("M8", ["persweep_orbslam.csv", "persweep_orbslam.tex"], 63, "column means = per-set means", "ok", True,
                 sorted(set(files)), None, f"window {window:g} s; ORB-SLAM3 from {rel(slam_dir)}")


def m9():
    return entry("M9", {
        "hand-eye": "rgbd-us/tools/merge_hand_eye.py: one T_marker_cam and one board pose fitted jointly by robust "
                    "least squares on the ChArUco corner positions of the still frames (< 5 deg/s) of calib_201 + "
                    "calib_202; 3.5 mm board-corner error. Not cv2.calibrateHandEye.",
        "orbslam3": "ORB_SLAM3/src/Tracking.cc, Tracking::Track(), localisation branch: "
                    "'if(mState==LOST)' -> 'if(mState==LOST || mState==RECENTLY_LOST)'; reloc mode sets "
                    "RECENTLY_LOST before every frame (Examples/RGB-D/rgbd_online.cc:110)",
        "for the user": "phantom manufacturer; sweep direction, length, plane orientation; ethics committee, date, number"},
        None, None, None, None, ["rgbd-us/note_RPR.md:81", "ORB_SLAM3: git diff src/Tracking.cc"], None,
        "lookup done by hand on 2026-11-20 (missing_numbers.md, 5.1)")


OCC_SETS = {"P-rearr1": "5XXB-exam", "P-rearr2": "5XXC-exam"}
OCC_LEVELS = {"none": "", "30 %": "-occ30", "60 %": "-occ60"}
OCC_MODES = ["online", "loc", "reloc"]
# rerun_plan.md section 3: these original runs stop before the end of the sequence; complete runs replace them
OCC_REPLACED = {("5XXC-exam-occ60", "loc"): "slam-5XXC-exam-occ60-loc-r4",
                ("5XXC-exam-occ60", "reloc"): "slam-5XXC-exam-occ60-reloc-r2",
                ("5XXB-exam-occ60", "reloc"): "slam-5XXB-exam-occ60-reloc-r2"}
# 2 s values of rerun_plan.md (section 7.1 of v3) that the item must reproduce before it reports
OCC_CHECK_OURS = {("P-rearr1", "30 %"): 5.15, ("P-rearr1", "60 %"): 5.25,
                  ("P-rearr2", "30 %"): 3.53, ("P-rearr2", "60 %"): 3.86}
OCC_CHECK_ORB_LOC = {("P-rearr1", "30 %"): 17.88, ("P-rearr1", "60 %"): 3.34, ("P-rearr2", "30 %"): 2.46}


def occ_shape(path, key):
    d = json.load(open(path))["sweeps"].get(key)
    return None if d is None else float(np.mean([v["shape"] for v in d.values()]))


def m11(window, slam_dir):
    """Occlusion, P-rearr1 and P-rearr2: ours and ORB-SLAM3 (full SLAM as tracked, localisation only, each frame
    relocalised) per occluder width; mean of per-sweep medians, worst sweep, shape, sweeps posed. ORB-SLAM3 values
    are single runs; the three stopped originals are replaced by the complete runs of rerun_plan.md section 3."""
    files, vals_, exp, got = [], {}, {}, {}
    ours_shape = RUNS / "paper_final" / "shape-occ-ours.json"
    files.append(rel(ours_shape))
    for name, sp in OCC_SETS.items():
        for lev, suf in OCC_LEVELS.items():
            folder = f"track-v2map-{sp}{suf}"
            files.append(f"runs/{folder}/scr_track.json")
            e = vals(track(folder, window))
            raw = json.load(open(RUNS / folder / "scr_track.json"))["per_sweep"]["raw"]
            rec = {"ours": {"mean": float(np.nanmean(e)), "worst": float(np.nanmax(e)),
                            "shape": occ_shape(ours_shape, f"{folder}|scr-track"),
                            "passed_gate_pct": float(np.mean([v["coverage_pct"] for v in raw.values()]))}}
            if (name, lev) in OCC_CHECK_OURS:
                exp[f"ours {name} {lev}"] = OCC_CHECK_OURS[(name, lev)]
                got[f"ours {name} {lev}"] = round(float(np.mean(vals(track(folder, 2.0)))), 2)
            for mode in OCC_MODES:
                split = f"{sp}{suf}"
                sub = OCC_REPLACED.get((split, mode))
                d = (RUNS / sub) if sub else (slam_dir / f"slam-{split}-{mode}")
                p = d / "slam_eval.json"
                files.append(rel(p))
                j = json.load(open(p))
                if j["args"]["smooth"] != window:
                    return failed("M11", f"smoothing {window:g} s", f"{rel(p)}: {j['args']['smooth']} s", files)
                s = np.array([v["us_median"] for v in j["sweeps"].values()], float)
                posed = int(np.sum(np.isfinite(s)))
                if sub and posed != len(s):
                    return failed("M11", "replacement run with every sweep posed", f"{sub}: {posed} / {len(s)}", files)
                rec[mode] = {"mean": float(np.nanmean(s)) if posed else None,
                             "worst": float(np.nanmax(s)) if posed else None,
                             "shape": occ_shape(d / "shape.json", f"{d.name}|orbslam3") if (d / "shape.json").exists() else None,
                             "sweeps_posed": f"{posed} / {len(s)}", "run": d.name}
                if mode == "loc" and (name, lev) in OCC_CHECK_ORB_LOC:
                    exp[f"loc {name} {lev}"] = OCC_CHECK_ORB_LOC[(name, lev)]
                    got[f"loc {name} {lev}"] = round(rec[mode]["mean"], 2)
            vals_[f"{name}, {lev}"] = rec
    if any(abs(got[k] - exp[k]) > 0.005 for k in exp):
        return failed("M11", exp, got, files)
    occluded = [k for k in vals_ if not k.endswith("none")]
    lower = [k for k in occluded if vals_[k]["loc"]["mean"] is not None and vals_[k]["loc"]["mean"] < vals_[k]["ours"]["mean"]]
    latex = {"ORB-SLAM3 localisation only lower mean": f"{len(lower)} of {len(occluded)} occluded settings ({', '.join(lower)})",
             "ours, increase over no occluder": ", ".join(
                 f"{k}: +{vals_[k]['ours']['mean'] - vals_[k.split(',')[0] + ', none']['ours']['mean']:.2f}" for k in occluded),
             "ours, worst sweep": f"{max(vals_[k]['ours']['worst'] for k in occluded):.1f}",
             "ours, passed the inlier gate": f"{min(vals_[k]['ours']['passed_gate_pct'] for k in occluded):.1f}--"
                                             f"{max(vals_[k]['ours']['passed_gate_pct'] for k in occluded):.1f} %"}
    return entry("M11", vals_, len(occluded), exp, got, True, sorted(set(files)), latex,
                 f"window {window:g} s; ORB-SLAM3 single runs; replaced: {', '.join(OCC_REPLACED.values())}")


# ---------------------------------------------------------------- report

def fmt(x):
    if isinstance(x, float):
        return f"{x:.4f}" if abs(x) < 0.01 and x != 0 else f"{x:.2f}"
    if isinstance(x, dict):
        return "; ".join(f"{k}: {fmt(v)}" for k, v in x.items())
    if isinstance(x, list):
        return "[" + ", ".join(fmt(v) for v in x) + "]"
    return str(x)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--window", type=float, default=2.0, help="offline smoothing window for the reported values (s)")
    ap.add_argument("--slam-dir", default="runs/paper_final",
                    help="folder with slam-<split>[-mode]/slam_eval.json at --window")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    slam_dir = (REPO / args.slam_dir) if not Path(args.slam_dir).is_absolute() else Path(args.slam_dir)

    items = []
    for f in (m1, lambda: m2(args.window), lambda: m3(args.window), m4, m5, lambda: m6(args.window)):
        items.append(f())
    e7, _ = m7(args.window, slam_dir)
    items.append(e7)
    items.append(m8(args.window, slam_dir, out))
    items.append(m9())
    items.append(entry("M10", "not run (optional)", None, None, None, None, ["runs/polaris-track.md"], None))
    items.append(m11(args.window, slam_dir))

    (out / "missing_numbers.json").write_text(json.dumps(items, indent=2, default=float) + "\n")
    md = [f"# Missing numbers (window {args.window:g} s, ORB-SLAM3 from `{rel(slam_dir)}`)", "",
          "| id | check | values | latex | note |", "|---|---|---|---|---|"]
    for it in items:
        chk = {True: "ok", False: "**CHECK FAILED**", None: "lookup"}[it["check_ok"]]
        if it["check_ok"] is False:
            chk += f" (expected {fmt(it['check_expected'])}, got {fmt(it['check_got'])})"
        cell = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
        md.append(f"| {it['id']} | {cell(chk)} | {cell(fmt(it['values']))} | {cell(fmt(it['latex']) if it['latex'] else '')} "
                  f"| {cell(it['note'])} |")
    (out / "missing_numbers_report.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print(f"-> {out}/missing_numbers.json, missing_numbers_report.md, persweep_orbslam.csv/.tex")
    if any(it["check_ok"] is False for it in items):
        sys.exit(1)


if __name__ == "__main__":
    main()
