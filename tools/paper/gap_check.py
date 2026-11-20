"""
rerun_plan.md, section 5.6: list every empty cell (--) of Tables III to V in paper/main.tex, with its group and
whether its source file exists. Read only: nothing is run, nothing in paper/ or runs/ is changed.

Groups (as in the plan):
  A  not applicable: fix by layout, no source needed
  B  probably computable from existing files: the source is checked, and the value is printed where it can be read
  C  real gap: a run would be needed (never ORB-SLAM3, decision D3)
  ?  no rule for this cell yet: source unknown

  python tools/paper/gap_check.py
  python tools/paper/gap_check.py --out runs/paper_final/numbers/gap_check.md
"""

import argparse
import glob
import json
import re
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[2]
RUNS = REPO / "runs"
TABLES = {"tab:test": "III", "tab:ctrl": "IV", "tab:baselines": "V"}
F2 = ["4XXA", "4XXB", "4XXC", "4XXD", "4XXE"]
F2_MAP = {"\\Fnew": "4XXA", "\\Fsmall": "4XXB", "\\Flarge": "4XXC", "\\Fsubj": "4XXC", "\\Farm": "4XXC"}
SET_SPLIT = {"\\Prearra": "5XXB", "\\Prearrb": "5XXC", "\\Ppeople": "5XXD", "\\Pempty": "5XXE"}


# ---------------------------------------------------------------- parsing

def strip_cell(c):
    return re.sub(r"\s+", " ", c).strip()


def tables(tex):
    """{label: (header cells, [(row label, cells)])} for the tables in TABLES."""
    out = {}
    for m in re.finditer(r"\\begin\{table\*?\}.*?\\end\{table\*?\}", tex, re.S):
        block = m.group(0)
        labels = re.findall(r"\\label\{(tab:[^}]*)\}", block)
        lab = next((l for l in labels if l in TABLES), None)
        if not lab:
            continue
        body = block[block.index("\\toprule") + 8:block.index("\\bottomrule")]
        lines = [l for l in re.split(r"\\\\", body)]
        rows, header, last = [], None, ""
        for l in lines:
            l = re.sub(r"(?<!\\)%.*", "", l)
            l = l.replace("\\midrule", "").replace("\\toprule", "")
            l = re.sub(r"\\cmidrule\([^)]*\)\{[^}]*\}", "", l)
            if not l.strip() or "\\multicolumn" in l and "&" not in l:
                continue
            cells = [strip_cell(c) for c in l.split("&")]
            if header is None:
                header = cells
                continue
            if cells[0]:
                last = cells[0]
            rows.append((last if not cells[0] else cells[0], cells))
        out[lab] = (header, rows)
    return out


# ---------------------------------------------------------------- reading sources

def exists(pattern):
    return sorted(glob.glob(str(REPO / pattern)))


def track_mean(folder, field="us_median", window="smoothed 2 s"):
    p = RUNS / folder / "scr_track.json"
    if not p.exists():
        return None
    d = json.load(open(p))["per_sweep"][window]
    v = [x[field] for x in d.values() if x[field] == x[field]]
    return float(np.mean(v)) if v else None


def slam_mean(folder, field):
    p = RUNS / "paper_final" / folder / "slam_eval.json"
    if not p.exists():
        return None
    v = [x[field] for x in json.load(open(p))["sweeps"].values() if x[field] == x[field]]
    return float(np.mean(v)) if v else None


def map_err(split):
    """Camera position error (median, mm) after the pose graph, from map_report.md."""
    p = RUNS / f"map-{split}" / "map_report.md"
    if not p.exists():
        return None
    for l in open(p):
        if l.startswith("| pose graph"):
            return float(l.split("|")[5].split("/")[0])
    return None


def f2(x):
    return "–" if x is None else f"{x:.2f}"


# ---------------------------------------------------------------- rules

def rule(tab, row, rowlabel, col, cells):
    """(group, source, value or note) for one empty cell."""
    first = cells[0]
    r = row
    if tab == "tab:test":
        if col == "Ref." and any(s in r for s in SET_SPLIT):
            s = next(SET_SPLIT[k] for k in SET_SPLIT if k in r)
            src = f"runs/track-v2-{s}-exam/scr_track.json"
            return "C", src, ("exists" if exists(src) else "no oracle checkpoint or track for this set (only P-ref has one)")
        if col in ("Map err.", "Seeds") and ("strict" in first or "real time" in first):
            return "A", "-", "same map as the row above / single seed"
        if col == "Ref." and "real time" in first:
            return "A", "-", "no oracle run in real time"
        if col in ("Ref.", "Map err.", "Seeds"):
            return "A", "-", "ablation row: column exists only for the headline rows"
    if tab == "tab:ctrl":
        if col == "Oracle":
            if "both scans" in r:
                return "C", "runs/track-v2-5XXA-both", "no oracle network on the merged map"
            if any(s in r for s in SET_SPLIT) or "after" in r or "map" in r:
                return "C", "runs/track-v2-5XX?-*", "no oracle checkpoint for these sets or maps"
            if any(o in r for o in ("none", "30", "60")):
                return "C", "runs/track-v2-5XX?-exam-occ*", "no oracle checkpoint for P-rearr1 / P-rearr2"
        if col == "Map err." and any(k in r for k in F2_MAP):
            s = next(F2_MAP[k] for k in F2_MAP if k in r)
            v = map_err(s)
            return "B", f"runs/map-{s}/map_report.md (pose graph, camera position)", f2(v)
        if col == "Map err." and "\\Ftwo" in r and "mean" in r:
            v = [map_err(F2_MAP[k]) for k in ("\\Fnew", "\\Fsmall", "\\Flarge", "\\Fsubj", "\\Farm")]
            return "B", "runs/map-4XX{A,B,C}/map_report.md", f2(float(np.mean(v)) if None not in v else None) + " (mean of the 5 sets)"
        if col == "Cov." and "after the sweeps" in r:
            src = "runs/map-5XXA-after/poses_room-503.json"
            return "B", src, ("poses exist; coverage needs the coverage computation (30 mm, 10 deg)" if exists(src) else "poses missing")
        if col == "Map err." and "'s map" in r:
            return "A", "-", "the map's own error is in the row of the set it was made on"
        if col in ("Cov.", "Map err.") and any(o in r for o in ("none", "30", "60")):
            return "A", "-", "same sweeps and map as the exam-view row of the set"
    if tab == "tab:baselines":
        if "Proposed" in first and col == "\\Fval":
            return "B", "runs/track-v2map-2XX/scr_track.json", f2(track_mean("track-v2map-2XX")) + " (2 s)"
        if "Proposed" in first and col == "Jitter":
            v = [track_mean(f"track-v2map-{s}", "step_8rows") for s in F2]
            return "B", "runs/track-v2map-4XX{A..E}/scr_track.json (step_8rows, 2 s)", \
                (f2(float(np.mean(v))) + " (F2, mean of the 5 sets)") if None not in v else "missing"
        if "ORB-SLAM3" in first and col in ("\\Fval", "Strict"):
            return "C", "runs/paper_final/slam-2XX* / strict sequence", "no ORB-SLAM3 run (D3: drop the cell)"
        if "ORB-SLAM3" in first and col == "Jitter":
            v = [slam_mean(f"slam-{s}-loc", "step_8rows") for s in F2]
            return "B", "runs/paper_final/slam-4XX{A..E}-loc/slam_eval.json (step_8rows, 2 s)", \
                (f2(float(np.mean(v))) + " (F2, mean of the 5 sets)") if None not in v else "missing"
        if "Classical, self-made" in first and col == "\\Fval":
            src = "runs/sys-classical-trackerfree-2XX"
            return ("B" if exists(src) else "C"), src, ("exists" if exists(src) else "no run")
        if "Pose regression" in first and col == "\\Fval":
            src = "runs/sys-learned-2XX"
            return "?", src, ("folder exists: check that it is the pose-regression system and read it"
                              if exists(src) else "no run")
    return "?", "-", "no rule: source unknown"


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tex", default=str(REPO / "paper" / "main.tex"))
    ap.add_argument("--out", default=None, help="also write the report to this markdown file")
    args = ap.parse_args()

    tex = open(args.tex).read()
    found = tables(tex)
    lines = ["# Empty cells (--) in Tables III to V", "",
             f"Source: `{args.tex}`. "
             "Group: A not applicable (layout), B computable from existing files, C a run would be needed, "
             "? no rule yet.", ""]
    count = {}
    for lab, num in TABLES.items():
        if lab not in found:
            lines += [f"Table {num} (`{lab}`) not found.", ""]
            continue
        header, rows = found[lab]
        lines += [f"## Table {num} (`{lab}`)", "", "| row | column | group | source | value / note |", "|---|---|---|---|---|"]
        for rowlabel, cells in rows:
            for j, c in enumerate(cells):
                if not re.search(r"(^|[\s/])--($|[\s/])", c) or j >= len(header):
                    continue
                full = cells[0] if lab == "tab:baselines" else " ".join(x for x in (rowlabel if not cells[0] else "", *cells[:2]) if x)
                g, src, note = rule(lab, full, rowlabel, header[j], cells)
                count[g] = count.get(g, 0) + 1
                lines.append(f"| {full} | {header[j]} | {g} | `{src}` | {note} |")
        lines.append("")
    lines.append("Total: " + ", ".join(f"{g} {n}" for g, n in sorted(count.items())) + f" ({sum(count.values())} cells)")
    text = "\n".join(lines) + "\n"
    print(text)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        open(args.out, "w").write(text)


if __name__ == "__main__":
    main()
