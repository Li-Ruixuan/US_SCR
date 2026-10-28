"""
Interactive 3D pages of compounded sweeps, one HTML file per sweep, straight from anchoring
results: the US volume compounded with the true poses (Polaris) and with each estimate, on one
common grid, rotatable in a browser (tools/volume_3d.py; MIP, overlay and translucent modes, path
of the US image centre, image outlines).

Two steps, chained:
  1. poses.py --source anchored-<mode>-<tag> exports each estimate per sweep as JSON
     (from the trajectories anchoring.py saved in <odometry arm>/preds/; CPU, no network);
  2. tools/volume_3d.py --json <one JSON per estimate> builds the page of each sweep.

--track adds the single-network system (scr_anchor.py track): its raw poses (<track dir>/poses.npz)
are smoothed with --track-window (2 s, the chosen window) at every row of the reference export (the
first --anchoring or --extra source) and written in the poses.py format, first on the page.

Every run also rewrites <parent of --out>/index.html: one table per split (sub-folder), one row per
sweep, the mean pixel error of each source and a link to its page.

--anchoring takes anchor_eval_<tag>.json files (from tools/anchoring_kabsch.py or anchoring.py):
the tag and the odometry arm are read from them, so no source name has to be typed. --extra adds
plain sources such as classical-vo-train_3XX (odometry only). The odometry run is the path stored in
the anchoring file; give --odometry if that path is not valid here (e.g. files written in rgbd-us with
relative paths).

  python tools/volume_pages.py --test-root $DATA/train_3XX --track runs/track-3XX \\
      --anchoring runs/sys-classical-r-3XX/anchor_eval_classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-train_3XX.json \\
      --extra classical-vo-train_3XX --out runs/volume3d/3XX
"""

import argparse
import glob
import html
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
TRACK = "scr-track"


def track_export(track_dir, ref_path, window, out_path):
    """The single-network trajectory of one sweep in the poses.py format, on the rows of a reference export."""
    sys.path.insert(0, str(REPO))
    from scr_anchor import smooth_poses
    ref = json.load(open(ref_path))
    z = np.load(Path(track_dir) / "poses.npz")
    sw = ref["run"]
    if f"{sw}_rows" not in z:
        return False
    pose = {int(r): (T, k) for r, T, k in zip(z[f"{sw}_rows"], z[f"{sw}_T"], z[f"{sw}_inl"])}
    T_cam_us = np.asarray(ref["T_cam_us"])
    frames = [dict(f) for f in ref["frames"]]
    for seg in sorted({f["segment"] for f in frames}):
        idx = [n for n, f in enumerate(frames) if f["segment"] == seg]
        rows = np.array([frames[n]["row"] for n in idx])
        T = np.array([pose[r][0] if r in pose else np.full((4, 4), np.nan) for r in rows])
        w = np.array([pose[r][1] if r in pose else 0 for r in rows], float)
        Ts = smooth_poses(np.array([frames[n]["t"] for n in idx]), T, w, window)
        for n, Tn in zip(idx, Ts):
            frames[n]["T_world_cam_pred"] = Tn.tolist()
            frames[n]["T_world_us_pred"] = (Tn @ T_cam_us).tolist()
    doc = dict(ref, source=TRACK, chaining=f"SCR alone on every frame, smoothed {window:g} s (scr_anchor.py track)",
               frames=frames)
    json.dump(doc, open(out_path, "w"))
    return True


def page_errors(page):
    """{label: mean pixel error} from a volume_3d.py page."""
    s = open(page).read()
    i = s.index("const META = ") + len("const META = ")
    meta = json.loads(s[i:s.index(";\n", i)])
    return {src["label"]: src["pixel_error_mm"] for src in meta["sources"] if src["key"] != "gt"}


def write_index(root):
    """<root>/index.html: per split folder, the mean pixel error of each source per sweep, with links."""
    root = Path(root)
    parts = ["<!doctype html><html><head><meta charset='utf-8'><title>3D pages</title><style>"
             "body{font-family:sans-serif;margin:24px;color:#222}table{border-collapse:collapse;margin-bottom:24px}"
             "td,th{border:1px solid #ccc;padding:4px 10px;text-align:right}th{background:#f2f2f2}"
             "td:first-child,th:first-child{text-align:left}tr.mean td{font-weight:bold;background:#fafafa}</style></head><body>",
             "<h1>3D pages: mean pixel error over the compounded US images (mm)</h1>"]
    for split in sorted(d for d in root.iterdir() if d.is_dir() and list(d.glob("run-*.html"))):
        pages = sorted(split.glob("run-*.html"))
        errs = {p.stem: page_errors(p) for p in pages}
        labels = list(dict.fromkeys(l for e in errs.values() for l in e))
        parts.append(f"<h2>{html.escape(split.name)}</h2><table><tr><th>sweep</th>"
                     + "".join(f"<th>{html.escape(l)}</th>" for l in labels) + "</tr>")
        for p in pages:
            parts.append(f"<tr><td><a href='{split.name}/{p.name}'>{p.stem}</a></td>"
                         + "".join(f"<td>{errs[p.stem].get(l, float('nan')):.1f}</td>" for l in labels) + "</tr>")
        parts.append("<tr class='mean'><td>mean</td>" + "".join(
            f"<td>{np.nanmean([e.get(l, np.nan) for e in errs.values()]):.1f}</td>" for l in labels) + "</tr></table>")
    (root / "index.html").write_text("\n".join(parts) + "</body></html>\n")
    print(f"index -> {root / 'index.html'}")


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


def run(cmd, dry, check=True):
    print("$ " + " ".join(str(c) for c in cmd), flush=True)
    if not dry:
        ok = subprocess.run([str(c) for c in cmd]).returncode == 0
        if not ok and check:
            raise SystemExit("the command above failed")
        return ok
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--test-root", required=True, help="e.g. data/train_3XX or data/test_4XXA (relative to rgbd-us)")
    ap.add_argument("--runs", nargs="+", default=None, help="sweeps (default: every sweep exported)")
    ap.add_argument("--anchoring", nargs="+", default=[], help="anchor_eval_<tag>.json files")
    ap.add_argument("--mode", default="pgo", choices=["pgo", "offline", "causal"],
                    help="which anchored trajectory: pose graph, offline or causal")
    ap.add_argument("--extra", nargs="+", default=[], help="plain poses.py sources, e.g. classical-vo-train_3XX, zero")
    ap.add_argument("--track", default=None, help="scr_anchor.py track folder: the single-network system, first on the page")
    ap.add_argument("--track-window", type=float, default=2.0, help="smoothing window of --track (s)")
    ap.add_argument("--track-label", default="one SCR network (ours)")
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
    if args.track and not args.dry_run:                 # the single-network system, on the rows of the first source
        for sweep in sweeps:
            ref = exported(sources[0][0], sweep)
            if ref and not track_export(args.track, ref, args.track_window, out / "poses" / f"fold0_{sweep}_{TRACK}.json"):
                print(f"{sweep}: not in {args.track}/poses.npz")
    if args.track:
        sources = [(TRACK, args.track_label)] + sources
    failed = []
    for sweep in sweeps:                                # 2. one page per sweep
        js = [exported(s, sweep) for s, _ in sources]
        if not args.dry_run and None in js:
            print(f"{sweep}: skipped, not exported for {[s for (s, _), j in zip(sources, js) if j is None]}")
            continue
        if not run([sys.executable, REPO / "tools" / "volume_3d.py", "--json", *[j or f"<{s}>" for (s, _), j in zip(sources, js)],
                    "--labels", *[l for _, l in sources], "--out", out / f"{sweep}.html",
                    "--voxel", args.voxel, "--stride", args.stride], args.dry_run, check=False):
            failed.append(sweep)
    print(f"pages -> {out}/<run>.html" + (f"; FAILED: {failed} (error above each)" if failed else ""))
    if not args.dry_run:
        write_index(out.parent)


if __name__ == "__main__":
    main()
