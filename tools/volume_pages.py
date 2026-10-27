"""
Interactive 3D pages of compounded sweeps, one HTML file per sweep, straight from anchoring
results: the US volume compounded with the true poses (Polaris) and with each estimate, on one
common grid, rotatable in a browser (tools/volume_3d.py; MIP, overlay and translucent modes, path
of the US image centre, image outlines).

Two steps, chained:
  1. poses.py --source anchored-<mode>-<tag> exports each estimate per sweep as JSON
     (from the trajectories anchoring.py saved in <odometry arm>/preds/; CPU, no network);
  2. tools/volume_3d.py --json <one JSON per estimate> builds the page of each sweep.

--anchoring takes anchor_eval_<tag>.json files (from tools/anchoring_kabsch.py or anchoring.py):
the tag and the odometry arm are read from them, so no source name has to be typed. --extra adds
plain sources such as classical-vo-train_3XX (odometry only). The odometry run is the path stored in
the anchoring file; give --odometry if that path is not valid here (e.g. files written in rgbd-us with
relative paths).

  python tools/volume_pages.py --test-root $DATA/train_3XX \\
      --anchoring runs/sys-final-3XX/anchor_eval_scr-v1-3XX-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX.json \\
      --extra classical-vo-train_3XX --out runs/volume3d-final/3XX
"""

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def anchoring_source(path, mode):
    """(source name for poses.py, odometry arm, label) of one anchor_eval_<tag>.json."""
    a = json.load(open(path))["args"]
    tag = Path(path).stem.removeprefix("anchor_eval_")
    odo = "classical odometry" if "odo-classical-vo" in tag else "RPRNet odometry"
    if a["anchor"] == "scr":
        what = f"SCR anchors ({Path(a['scr_ckpt']).parent.name})"
    else:
        what = "classical anchors" if a["anchor"] == "classical" else "anchor network"
    return f"anchored-{mode}-{tag}", a["odometry"], f"{what} + {odo}" + ("" if mode == "pgo" else f" ({mode})")


def extra_label(source):
    if source.startswith("classical-vo"):
        return "classical odometry only"
    return {"zero": "zero motion", "model": "RPRNet odometry only"}.get(source, source)


def run(cmd, dry):
    print("$ " + " ".join(str(c) for c in cmd), flush=True)
    if not dry:
        subprocess.run([str(c) for c in cmd], check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-root", required=True, help="e.g. data/train_3XX or data/test_4XXA (relative to rgbd-us)")
    ap.add_argument("--runs", nargs="+", default=None, help="sweeps (default: every sweep exported)")
    ap.add_argument("--anchoring", nargs="+", default=[], help="anchor_eval_<tag>.json files")
    ap.add_argument("--mode", default="pgo", choices=["pgo", "offline", "causal"],
                    help="which anchored trajectory: pose graph, offline or causal")
    ap.add_argument("--extra", nargs="+", default=[], help="plain poses.py sources, e.g. classical-vo-train_3XX, zero")
    ap.add_argument("--labels", nargs="+", default=None, help="one per --anchoring, then one per --extra")
    ap.add_argument("--odometry", default=None, help="odometry arm (default: from the anchoring files)")
    ap.add_argument("--out", required=True, help="folder for <run>.html (and the exported JSON in poses/)")
    ap.add_argument("--voxel", type=float, default=1.0)
    ap.add_argument("--stride", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true", help="print the commands only")
    args = ap.parse_args()

    sources = [anchoring_source(p, args.mode) for p in args.anchoring]
    odo = args.odometry or (sources[0][1] if sources else None)
    if odo is None:
        raise SystemExit("give --odometry when there is no --anchoring file")
    if len({Path(o).name for _, o, _ in sources}) > 1:          # compare the arm, not where it is stored
        raise SystemExit("the anchoring files use different odometry arms; one page needs one")
    sources = [(s, l) for s, _, l in sources] + [(s, extra_label(s)) for s in args.extra]
    if args.labels:
        if len(args.labels) != len(sources):
            raise SystemExit(f"--labels needs {len(sources)} labels")
        sources = [(s, l) for (s, _), l in zip(sources, args.labels)]

    out = Path(args.out).resolve()
    ckpts = sorted(glob.glob(str(Path(odo) / "fold*" / "best.pt")))
    if not ckpts and not args.dry_run:
        raise SystemExit(f"no {odo}/fold*/best.pt: give the odometry run with --odometry")
    for src, _ in sources:                              # 1. export (CPU, from the saved trajectories)
        cmd = [sys.executable, REPO / "poses.py", "--ckpts", *ckpts, "--source", src, "--test-root", args.test_root,
               "--out", out, "--no-plot", "--no-compound"]
        run(cmd + (["--test-runs", *args.runs] if args.runs else []), args.dry_run)

    def exported(src, sweep):
        f = sorted(glob.glob(str(out / "poses" / f"fold*_{sweep}_{src}.json")))
        return f[0] if f else None

    sweeps = args.runs or sorted({Path(p).name.split("_")[1] for p in glob.glob(str(out / "poses" / "fold*_*.json"))})
    for sweep in sweeps:                                # 2. one page per sweep
        js = [exported(s, sweep) for s, _ in sources]
        if not args.dry_run and None in js:
            print(f"{sweep}: skipped, not exported for {[s for (s, _), j in zip(sources, js) if j is None]}")
            continue
        run([sys.executable, REPO / "tools" / "volume_3d.py", "--json", *[j or f"<{s}>" for (s, _), j in zip(sources, js)],
             "--labels", *[l for _, l in sources], "--out", out / f"{sweep}.html",
             "--voxel", args.voxel, "--stride", args.stride], args.dry_run)
    print(f"pages -> {out}/<run>.html")


if __name__ == "__main__":
    main()
