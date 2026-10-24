"""
Does room-scan coverage explain the SCR anchor errors? For every evaluated sweep frame in one or
more scr_eval.json files (scr_anchor.py eval): the distance to the nearest room-scan camera pose of
the map the checkpoint was trained on, and whether the frame is covered in the sense of rgbd-us
tools/check_coverage.py (some room-scan pose within 30 mm and 10 deg). Then the anchor error per
distance bin and covered / not covered, per eval file and pooled. Poses only, no images: seconds.

  python tools/coverage_error.py runs/v1-*/eval_*/scr_eval.json runs/s1-e120-2XX/eval_*/scr_eval.json
"""

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import numpy as np                                          # noqa: E402

from dataloader import load_hand_eye                         # noqa: E402
from geometry import compose, load_marker_poses              # noqa: E402

BINS = [0, 30, 60, 100, 200, np.inf]                         # mm to the nearest room-scan pose


def camera_poses(run_dir, T_mc):
    T_wm, valid, _ = load_marker_poses(Path(run_dir) / "frames.csv", "mm")
    return compose(T_wm, T_mc), valid


def hand_eye_path(path):
    p = Path(path)
    return p if p.exists() else REPO / "T_marker_cam.npy"


def frame_coverage(eval_json):
    """Per solved frame: (error mm, nearest room-scan distance mm, covered)."""
    ev = json.load(open(eval_json))
    ck_dir = Path(ev["args"]["ckpt"]).parent
    if not (ck_dir / "config.json").exists():               # run from elsewhere: eval_* sits in the run folder
        ck_dir = Path(eval_json).parents[1]
    cfg = json.load(open(ck_dir / "config.json"))["args"]
    T_mc = load_hand_eye(hand_eye_path(cfg["hand_eye"]), "mm")

    scan = []
    for n in cfg["scan_runs"]:
        T, ok = camera_poses(Path(cfg["root"]) / n, T_mc)
        scan.append(T[ok])
    scan = np.concatenate(scan)
    sweeps = {}
    out = []
    for f in ev["frames"]:
        if not f["solved"]:
            continue
        if f["run"] not in sweeps:
            sweeps[f["run"]] = camera_poses(Path(ev["args"]["test_root"]) / f["run"], T_mc)[0]
        T = sweeps[f["run"]][f["row"]]
        dist = np.linalg.norm(scan[:, :3, 3] - T[:3, 3], axis=1)
        cos = (np.einsum("nij,ij->n", scan[:, :3, :3], T[:3, :3]) - 1) / 2       # trace(R_s^T R)
        ang = np.degrees(np.arccos(np.clip(cos, -1, 1)))
        out.append((f["err_mm"], float(dist.min()), bool(((dist < 30) & (ang < 10)).any())))
    return np.array(out, dtype=float).reshape(-1, 3)


def table(name, a):
    lines = [f"### {name}", "", "| nearest room-scan pose | frames | anchor error mm (median / p90) |", "|---|---|---|"]
    for lo, hi in zip(BINS[:-1], BINS[1:]):
        e = a[(a[:, 1] >= lo) & (a[:, 1] < hi), 0]
        rng = f"{lo:g}–{hi:g} mm" if np.isfinite(hi) else f"> {lo:g} mm"
        lines.append(f"| {rng} | {len(e)} | " + (f"{np.median(e):.1f} / {np.percentile(e, 90):.1f} |" if len(e) else "– |"))
    for label, sel in (("covered (≤ 30 mm and 10°)", a[:, 2] > 0), ("not covered", a[:, 2] == 0)):
        e = a[sel, 0]
        lines.append(f"| **{label}** | {len(e)} ({100 * len(e) / max(len(a), 1):.0f} %) | "
                     + (f"{np.median(e):.1f} / {np.percentile(e, 90):.1f} |" if len(e) else "– |"))
    return lines + [""]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("evals", nargs="+", help="scr_eval.json files")
    ap.add_argument("--out", default="runs/coverage_error.md")
    args = ap.parse_args()
    md, pooled = ["# SCR anchor error against room-scan coverage", ""], []
    for p in args.evals:
        a = frame_coverage(p)
        name = f"{Path(p).parents[1].name} / {Path(p).parent.name}"
        md += table(name, a)
        pooled.append(a)
        print(f"{name}: {len(a)} frames, {100 * a[:, 2].mean():.0f} % covered", flush=True)
    if len(pooled) > 1:
        md += table("all files pooled", np.concatenate(pooled))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text("\n".join(md))
    print("\n".join(md) + f"\n-> {args.out}")


if __name__ == "__main__":
    main()
