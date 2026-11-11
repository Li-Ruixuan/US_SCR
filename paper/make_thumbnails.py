"""
Thumbnails for the system overview (paper/fig_overview.tex): one real S-test frame as RGB, its aligned depth (perceptual
colormap, near = dark, no depth = light grey) and the network's room coordinates for the same frame
(x, y, z of each 16 x 16-pixel cell, each normalised to 0..1 over the frame and shown as R, G, B).

Step 1, pick a frame without people: a contact sheet of every --step-th row of a run
  python paper/make_thumbnails.py sheet --root $DATA/train_3XX --run room-301 --step 60
  -> paper/figures/thumbs/sheet_room-301.jpg (row numbers printed on each tile)

Step 2, the three thumbnails (training PC, GPU optional)
  python paper/make_thumbnails.py thumbs --root $DATA/train_3XX --run room-301 --row 900 \
      --ckpt runs/repro/v2map-3XX/best.pt
  -> paper/figures/thumbs/thumb_rgb.png, thumb_depth.png, thumb_coords.png (16:9, 600 dpi at 1.1 in wide)
"""

import argparse
import json
import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
OUT = Path(__file__).resolve().parent / "figures" / "thumbs"
MEAN = np.array([0.485, 0.456, 0.406], np.float32)      # = dataloader.IMAGENET_MEAN / STD
STD = np.array([0.229, 0.224, 0.225], np.float32)


def crop169(im):
    h, w = im.shape[:2]
    if abs(w / h - 16 / 9) < 0.01:
        return im
    if w / h > 16 / 9:
        nw = int(round(h * 16 / 9))
        return im[:, (w - nw) // 2:(w - nw) // 2 + nw]
    nh = int(round(w * 9 / 16))
    return im[(h - nh) // 2:(h - nh) // 2 + nh]


def frames(root, run):
    df = pd.read_csv(Path(root) / run / "frames.csv")
    return df


def sheet(args):
    d = Path(args.root) / args.run
    df = frames(args.root, args.run)
    rows = list(range(0, len(df), args.step))
    tiles = []
    for r in rows:
        im = cv2.imread(str(d / df["rgb"].iloc[r]))
        if im is None:
            continue
        im = cv2.resize(crop169(im), (320, 180), interpolation=cv2.INTER_AREA)
        cv2.putText(im, str(r), (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        tiles.append(im)
    cols = 6
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    grid = np.vstack([np.hstack(tiles[i:i + cols]) for i in range(0, len(tiles), cols)])
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / f"sheet_{args.run}.jpg"
    cv2.imwrite(str(p), grid, [cv2.IMWRITE_JPEG_QUALITY, 85])
    print(f"{len(rows)} frames of {args.run} (rows {rows[0]}..{rows[-1]}, every {args.step}) -> {p}")


def save(name, img_rgb, width_px):
    h = int(round(width_px * 9 / 16))
    img = cv2.resize(img_rgb, (width_px, h), interpolation=cv2.INTER_AREA if img_rgb.shape[1] > width_px else cv2.INTER_NEAREST)
    p = OUT / name
    cv2.imwrite(str(p), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    print(f"-> {p} ({width_px} x {h})")


def thumbs(args):
    import torch
    from matplotlib import cm
    from scr_anchor import load_model

    d = Path(args.root) / args.run
    df = frames(args.root, args.run)
    info = json.load(open(d / "camera_info.json"))
    scale = float(info.get("depth_scale", 0.001)) * 1000.0           # depth units -> mm
    rgb = cv2.cvtColor(cv2.imread(str(d / df["rgb"].iloc[args.row])), cv2.COLOR_BGR2RGB)
    dep = cv2.imread(str(d / df["depth"].iloc[args.row]), cv2.IMREAD_UNCHANGED).astype(np.float32) * scale
    print(f"{args.run} row {args.row}: {df['rgb'].iloc[args.row]}, {rgb.shape[1]} x {rgb.shape[0]}, depth scale {scale:g} mm/unit")
    OUT.mkdir(parents=True, exist_ok=True)
    wpx = int(round(args.width_in * args.dpi))

    # RGB
    save("thumb_rgb.png", crop169(rgb), wpx)

    # depth: near = dark (viridis), invalid (0 or out of 0.1-2 m) light grey
    valid = (dep > 100) & (dep < args.max_depth)
    lo, hi = np.percentile(dep[valid], [2, 98])
    col = (cm.get_cmap("viridis")(np.clip((dep - lo) / (hi - lo), 0, 1))[..., :3] * 255).astype(np.uint8)
    col[~valid] = 230
    save("thumb_depth.png", crop169(col), wpx)
    print(f"   depth shown {lo:.0f}-{hi:.0f} mm, {100 * (~valid).mean():.0f} % without depth")

    # network: room coordinates per cell
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    net, ck = load_model(args.ckpt, dev)
    H, W = ck.get("image_size", [360, 640])
    x = cv2.resize(rgb.astype(np.float32) / 255, (W, H), interpolation=cv2.INTER_AREA)
    x = torch.from_numpy(((x - MEAN) / STD).transpose(2, 0, 1)[None]).to(dev)
    with torch.no_grad():
        y = net(x)[0].float().cpu().numpy()                              # (3, H/8, W/8), m from the scene centre
    xyz = y.transpose(1, 2, 0)
    lo, hi = np.percentile(xyz.reshape(-1, 3), [2, 98], axis=0)
    c = (np.clip((xyz - lo) / (hi - lo), 0, 1) * 255).astype(np.uint8)
    save("thumb_coords.png", crop169(c), wpx)                         # nearest-neighbour upsampling keeps the cells
    print(f"   coordinates {xyz.shape[1]} x {xyz.shape[0]} cells, ranges (m) x {lo[0]:.2f}..{hi[0]:.2f}, "
          f"y {lo[1]:.2f}..{hi[1]:.2f}, z {lo[2]:.2f}..{hi[2]:.2f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sheet")
    s.add_argument("--root", required=True), s.add_argument("--run", required=True)
    s.add_argument("--step", type=int, default=60)
    t = sub.add_parser("thumbs")
    t.add_argument("--root", required=True), t.add_argument("--run", required=True)
    t.add_argument("--row", type=int, required=True)
    t.add_argument("--ckpt", required=True)
    t.add_argument("--max-depth", type=float, default=2000.0, help="mm")
    t.add_argument("--width-in", type=float, default=1.1, help="printed width of a thumbnail")
    t.add_argument("--dpi", type=int, default=600)
    args = ap.parse_args()
    sheet(args) if args.cmd == "sheet" else thumbs(args)


if __name__ == "__main__":
    main()
