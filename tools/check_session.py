"""
Check a recorded session after rgbd-us tools/match_streams.py: one line per recording, warnings at the end.

Per recording (frames.csv + match_report.json, written by match_streams.py):
  frames, length, RGB rate; marker: % of frames with a Polaris pose and the longest loss; pose clock offset
  and its gyro correlation; US: % of frames with a US image, probe in the air at the start; depth (aligned
  to RGB, every --every-th frame): % of pixels with depth and % within 0.1-2 m (what the labels and the
  Kabsch fit use), and the frames with almost no usable depth; Polaris: median marker distance along the
  tracker axis and % of frames nearer than --polaris-near (the Vega volume starts at about 0.95 m; nearer, the
  ground truth is not specified). tools/check_polaris.py checks the tracker in more detail.

  python tools/check_session.py --root /data2/u0137815/rgbd-us/data/train_5XX
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


def depth_stats(run, paths, near, far):
    valid, usable = [], []
    for p in paths:
        z = cv2.imread(str(run / p), cv2.IMREAD_UNCHANGED)
        if z is None:
            continue
        valid.append(float((z > 0).mean()))
        usable.append(float(((z > near) & (z < far)).mean()))
    return np.array(valid), np.array(usable)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="session folder with room-* and run-* recordings")
    ap.add_argument("--every", type=int, default=15, help="depth: check every n-th frame")
    ap.add_argument("--near", type=float, default=100.0, help="mm")
    ap.add_argument("--far", type=float, default=2000.0, help="mm (label limit)")
    ap.add_argument("--polaris-near", type=float, default=950.0, help="mm: start of the Polaris volume")
    ap.add_argument("--polaris-far", type=float, default=2400.0, help="mm: end of the Polaris volume")
    ap.add_argument("--out", default=None, help="also write the table to this .md")
    args = ap.parse_args()

    root = Path(args.root)
    runs = sorted(p for p in root.iterdir() if p.is_dir() and p.name.split("-")[0] in ("room", "run"))
    head = ("| recording | frames | s | Hz | marker % | longest loss s | clock offset ms (corr) | US % | air at start s "
            "| depth % | depth 0.1-2 m % (p10) | frames < 10 % usable | Polaris distance mm | outside volume % |")
    lines = [head, "|" + "---|" * (head.count("|") - 1)]
    warn = []
    for run in runs:
        n = run.name
        if not (run / "frames.csv").exists():
            lines.append(f"| {n} | not matched | | | | | | | | | | | | |")
            warn.append(f"{n}: no frames.csv (run match_streams.py)")
            continue
        d = pd.read_csv(run / "frames.csv")
        rep = json.load(open(run / "match_report.json")) if (run / "match_report.json").exists() else {}
        t = d["timestamp"].to_numpy(float)
        dur = float(t[-1] - t[0]) if len(t) > 1 else 0.0
        marker = 100.0 * float(d["tx"].notna().mean())
        lost = rep.get("pose_lost") or []
        longest = max((g for _, g in lost), default=0.0)
        off, corr = rep.get("pose_offset_ms"), rep.get("pose_gyro_corr")
        clock = f"{off:+.0f} ({corr:.2f})" if off is not None and corr is not None else "–"
        sweep = n.startswith("run-")
        us = 100.0 * float(d["us"].notna().mean()) if sweep else None
        air = (rep.get("us_air_s") or {}).get("start") if sweep else None
        valid, usable = depth_stats(run, d["depth"].dropna().iloc[::args.every], args.near, args.far)
        p = d[["tx", "ty", "tz"]].dropna().to_numpy(float)
        if len(p) and np.median(np.abs(p)) < 10:                       # metres -> mm
            p = p * 1000.0
        z = -p[:, 2]                                                   # in front of the Polaris: -z
        dist = f"{np.median(z):.0f}" if len(z) else "–"
        outside = 100.0 * float(((z < args.polaris_near) | (z > args.polaris_far)).mean()) if len(z) else 0.0
        low = 100.0 * float((usable < 0.10).mean()) if len(usable) else 100.0
        lines.append(f"| {n} | {len(d)} | {dur:.1f} | {len(d) / max(dur, 1e-9):.1f} | {marker:.1f} | {longest:.2f} | {clock} | "
                     f"{'' if us is None else f'{us:.0f}'} | {'' if air is None else f'{air:.1f}'} | "
                     f"{100 * valid.mean():.0f} | {100 * usable.mean():.0f} ({100 * np.percentile(usable, 10):.0f}) | {low:.0f} % | "
                     f"{dist} | {outside:.0f} |")
        if outside > 10:
            warn.append(f"{n}: marker outside the Polaris volume ({args.polaris_near / 1000:.2f}-{args.polaris_far / 1000:.1f} m "
                        f"along its axis) in {outside:.0f} % of the frames, median {dist} mm: ground truth not specified "
                        "there; next time keep the probe 1.0-2.0 m from the Polaris")
        if marker < (95 if sweep else 90):
            warn.append(f"{n}: marker only {marker:.1f} % (longest loss {longest:.1f} s): fewer frames to evaluate")
        if corr is not None and corr < 0.5:
            warn.append(f"{n}: pose clock offset not reliable (gyro correlation {corr:.2f}); offset not applied")
        if sweep and us is not None and us < 95:
            warn.append(f"{n}: US in only {us:.0f} % of the frames")
        if len(usable) and usable.mean() < 0.3:
            warn.append(f"{n}: little usable depth ({100 * usable.mean():.0f} % of pixels within "
                        f"{args.near / 1000:.1f}-{args.far / 1000:.0f} m): SCR labels and the Kabsch fit will be weak")
        if low > 10:
            warn.append(f"{n}: {low:.0f} % of the checked frames have < 10 % usable depth (likely no pose there)")
        if rep.get("rgb_without_depth", 0) > 0.02 * max(rep.get("rgb_frames", 1), 1):
            warn.append(f"{n}: {rep['rgb_without_depth']} RGB frames without depth were left out")
    text = "\n".join(lines) + "\n\n" + ("\n".join(f"- {w}" for w in warn) if warn else "- no warnings") + "\n"
    print(text)
    if args.out:
        Path(args.out).write_text(f"# Session check: {root}\n\n{text}")
        print(f"-> {args.out}")


if __name__ == "__main__":
    main()
