"""
Export slices of the compounded US volumes for the Probe Pose Viewer page.

Reads the volumes poses.py already wrote (<arm>/compound/fold<k>_<run>_<source>/volumes.npz:
GT-pose and estimated-pose volume on the same grid, 1 mm voxels) and writes, per held-out
sweep, evenly spaced slices along each world axis for

    gt        US images stacked with the Polaris poses
    odometry  stacked with the odometry poses          (source "model")
    anchored  stacked with odometry + learned anchors  (source "anchored-offline-...")

plus |estimate - GT| difference slices, as small JPEGs (base64), one JSON per sweep plus
index.json with the volume metrics from metrics.json. No network, no GPU.

  # from the repo root
  python tools/volume_viewer.py --anchored anchored-pgo-anchor-rgbd-v2-reg-odometry --out runs/volume-viewer-pgo
  python tools/volume_viewer.py --slices 13 ...    # more slices per axis

Caveat: the grid is the GT volume + 5 mm (poses.py), so estimated-pose pixels that fall
outside it are dropped. Large errors therefore show as missing anatomy, not displaced anatomy.
"""

import argparse
import base64
import json
from pathlib import Path

import cv2
import numpy as np


def png(img, color=False, quality=85):
    """Slice -> base64 JPEG (PNG of speckle is ~4x larger; the page loads one sweep at a time)."""
    if color:
        img = cv2.applyColorMap(img, cv2.COLORMAP_INFERNO)
    ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode()


def slice_positions(mask, axis, n):
    """n indices along `axis`, evenly spread over where the GT volume has data."""
    other = tuple(a for a in range(3) if a != axis)
    filled = mask.mean(axis=other)
    idx = np.flatnonzero(filled > 0.01 * filled.max())
    lo, hi = idx[0], idx[-1]
    return [int(round(x)) for x in np.linspace(lo + 0.05 * (hi - lo), hi - 0.05 * (hi - lo), n)]


def take(vol, axis, i):
    s = np.take(vol, i, axis=axis)
    return np.clip(s, 0, 255).astype(np.uint8).T[::-1]      # rows = second remaining axis, up = +


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", default="runs/rpr-rgb-gap4")
    ap.add_argument("--odometry", default="model")
    ap.add_argument("--anchored", default="anchored-offline-anchor-rgbd-v2-reg-odometry")
    ap.add_argument("--slices", type=int, default=9, help="slices per axis")
    ap.add_argument("--out", default="runs/volume-viewer", help="folder: index.json + one <run>.json per sweep")
    args = ap.parse_args()

    comp = Path(args.arm) / "compound"
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {"axes": ["x", "y", "z"], "voxel_mm": None, "sources": ["gt", "odometry", "anchored"],
           "image_format": "jpeg", "sweeps": {}}
    for odo_dir in sorted(comp.glob(f"fold*_*_{args.odometry}")):
        fold, run = odo_dir.name.split("_")[:2]
        anc_dir = comp / f"{fold}_{run}_{args.anchored}"
        if not (odo_dir / "volumes.npz").exists() or not (anc_dir / "volumes.npz").exists():
            print(f"skip {run}: volumes.npz missing for one of the sources")
            continue
        vo, va = np.load(odo_dir / "volumes.npz"), np.load(anc_dir / "volumes.npz")
        if vo["gt"].shape != va["gt"].shape or not np.allclose(vo["origin"], va["origin"]):
            raise SystemExit(f"{run}: odometry and anchored volumes are on different grids")
        gt, mg = vo["gt"], vo["mask_gt"]
        vols = {"gt": gt, "odometry": vo["pred"], "anchored": va["pred"]}
        masks = {"odometry": vo["mask_pred"], "anchored": va["mask_pred"]}
        out["voxel_mm"] = float(vo["voxel"])
        sw = {"fold": int(fold[4:]), "shape": list(gt.shape),
              "metrics": {k: json.load(open(d / "metrics.json")) for k, d in
                          (("odometry", odo_dir), ("anchored", anc_dir))},
              "slices": {}}
        for axis, name in enumerate(out["axes"]):
            rows = []
            for i in slice_positions(mg, axis, args.slices):
                r = {"index": i, "mm": float(vo["origin"][axis] + (i + 0.5) * vo["voxel"])}
                for src, v in vols.items():
                    r[src] = png(take(v, axis, i))
                for src in ("odometry", "anchored"):
                    union = np.take(mg | masks[src], i, axis=axis)
                    d = np.abs(np.take(vols[src], i, axis=axis) - np.take(gt, i, axis=axis)) * union
                    r[f"diff_{src}"] = png(np.clip(d, 0, 255).astype(np.uint8).T[::-1], color=True)
                rows.append(r)
            sw["slices"][name] = rows
        json.dump(sw, open(out_dir / f"{run}.json", "w"))
        m = sw["metrics"]
        out["sweeps"][run] = {"fold": sw["fold"], "file": f"{run}.json", "shape": sw["shape"],
                              "ncc": {s: m[s]["volume"]["ncc_union"] for s in m},
                              "dice": {s: m[s]["volume"]["dice"] for s in m},
                              "pixel_error_mm": {s: m[s]["pixel_error_mm"]["mean"] for s in m}}
        print(f"{run}: grid {gt.shape} | NCC odometry {m['odometry']['volume']['ncc_union']:.3f}, "
              f"anchored {m['anchored']['volume']['ncc_union']:.3f} | "
              f"{(out_dir / f'{run}.json').stat().st_size / 1e6:.1f} MB")
    json.dump(out, open(out_dir / "index.json", "w"), indent=1)
    print(f"wrote {out_dir}/index.json + {len(out['sweeps'])} sweep files")


if __name__ == "__main__":
    main()
