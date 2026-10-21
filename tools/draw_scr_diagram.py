"""
Draw the scene coordinate regression (SCR) anchor diagram (scr.py, note §2 and §6.6), in the style
of tools/draw_diagram.py: left the network and its training, right how a pose is computed from
its output and used in the system.

  python tools/draw_scr_diagram.py                 # -> tools/scr_diagram.png and .pdf
  python tools/draw_scr_diagram.py --out figures/scr_diagram

Colours: purple = the network (learned), green = training only, orange = geometry / arithmetic,
no learning, white = result. The numbers in the last box are the results of 20 Oct 2026
(§6.6); update them when the results change.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK, MUTED, RULE = "#1f1f1e", "#6b6a64", "#c9c8c0"
NET = ("#ece9fb", "#5b47c7")        # fill, edge: the network
TRAIN = ("#dff4ea", "#178a5e")      # training only
POST = ("#fff2dc", "#b8770b")       # geometry / arithmetic, no learning
OUT = ("#ffffff", "#1f1f1e")        # result

fig = plt.figure(figsize=(16, 9.8), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 160)
ax.set_ylim(0, 96)
ax.axis("off")


def box(x, y, w, h, title, sub="", style=NET, dashed=False, fs=11):
    fill, edge = style
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.2",
                                fc=fill, ec=edge, lw=1.6, ls="--" if dashed else "-"))
    n = sub.count("\n") + 1 if sub else 0
    ty = y + h / 2 + (0.95 * n + 0.6 if sub else 0)
    ax.text(x + w / 2, ty, title, ha="center", va="center", fontsize=fs, color=INK, weight="bold")
    if sub:
        ax.text(x + w / 2, ty - 1.9 - 0.95 * (n - 1), sub, ha="center", va="center", fontsize=8.6,
                color=MUTED, linespacing=1.35)


def arrow(x1, y1, x2, y2, color=MUTED, dashed=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12,
                                 color=color, lw=1.3, ls="--" if dashed else "-"))


# ---------------- left: the network and its training ----------------
ax.text(2, 93, "SCR network: the room coordinate of every pixel", fontsize=15, weight="bold", color=INK)
ax.text(2, 89.6, "one model per room scan; it predicts where in the room (mm) each image cell lies, not a pose",
        fontsize=9.5, color=MUTED)

box(2, 76, 36, 8, "RGB frame", "360 x 640, ImageNet-normalised\n(room-scan frame in training, sweep frame in use)")

box(2, 62, 36, 8, "Encoder, low", "EfficientNet-B0 stages 1-4 (ImageNet start)\nstride 8, 40 channels, fine-tuned")
arrow(20, 76, 20, 70.4)
box(44, 62, 30, 8, "Encoder, high", "stages 5-6: stride 16, 112 channels\nupsampled x2 (bilinear): wider context")
arrow(38.4, 66, 43.6, 66)

box(2, 48, 72, 8, "Concatenate per cell", "40 + 112 = 152 channels on the stride-8 grid (45 x 80 cells)")
arrow(20, 62, 20, 56.4)
arrow(59, 62, 59, 56.4)

box(2, 34, 72, 8, "Coordinate head", "1x1 convs 152 -> 256 -> 256 -> 256 -> 3 (ReLU): each cell on its own, no pooling")
arrow(38, 48, 38, 42.4)

box(2, 18, 72, 10, "Room coordinates", "45 x 80 cells x (x, y, z), metres from the scene centre\n= 3600 predicted 3D points per frame")
arrow(38, 34, 38, 28.4)

# training branch: targets from the room scan, loss against the predicted coordinates
box(2, 3.5, 72, 9.5, "Training targets (room scan only)",
    "room-scan depth at each cell centre, back-projected with the room-scan pose\n"
    "(Polaris here, SLAM in a new room); Huber loss on the 3D error, 15 epochs",
    TRAIN, fs=10.5)
arrow(38, 13.4, 38, 17.6, color=TRAIN[1])
ax.text(39.5, 15.4, "loss", fontsize=8.5, color=TRAIN[1], va="center")

# legend
lx, ly = 2, 0.2
for i, (style, lab) in enumerate([(NET, "network (learned)"), (TRAIN, "training only"),
                                  (POST, "geometry, no learning"), (OUT, "result")]):
    xx = lx + i * 22
    ax.add_patch(FancyBboxPatch((xx, ly), 3, 2.0, boxstyle="round,pad=0.1", fc=style[0], ec=style[1], lw=1.4))
    ax.text(xx + 4, ly + 1.0, lab, fontsize=8.8, va="center", color=INK)

# divider
ax.plot([90, 90], [4, 92], color=RULE, lw=1)

# ---------------- right: pose and use ----------------
ax.text(94, 93, "From coordinates to a camera pose", fontsize=15, weight="bold", color=INK)
ax.text(94, 89.6, "geometry decides: wrong predictions (moved objects, hands, glare) become outliers",
        fontsize=9.5, color=MUTED)

box(94, 74, 64, 10, "2D-3D pairs", "each cell centre in the full-resolution image (pixel)\n"
    "paired with its predicted room coordinate (mm): 3600 pairs", POST, fs=11.5)
ax.plot([74.4, 86, 86], [23, 23, 79], color=MUTED, lw=1.3)        # elbow: coordinates -> 2D-3D pairs
arrow(86, 79, 93.6, 79)

box(94, 58, 64, 10, "PnP + RANSAC", "camera pose that projects most room points onto their pixels\n"
    "within 10 px; >= 30 inliers, else no anchor; refined on the inliers", POST, fs=11.5)
arrow(126, 74, 126, 68.4)

box(94, 42, 64, 10, "Absolute camera pose in the room", "no keyframes, no retrieval, no prior pose:\n"
    "an anchor every 1 s, and the start pose of a sweep", POST, fs=11.5)
arrow(126, 58, 126, 52.4)

box(94, 26, 64, 10, "Combine with odometry", "classical odometry (SIFT + PnP-RANSAC between frames)\n"
    "+ anchors: offline pose graph, or reset for live use", POST, fs=11.5)
arrow(126, 42, 126, 36.4)

box(94, 8, 64, 12, "Pose of every US frame",
    "anchors: 9.8 mm (3XX), 16-26 mm (4XX); classical anchors 2.6-7 mm\n"
    "at the US image: 6.5 mm (3XX), 12-21 mm (4XX)\n"
    "classical anchors + classical odometry: 3.3 mm (3XX), 3.6-7.0 mm (4XX)", OUT, fs=11.5)
arrow(126, 26, 126, 20.4)

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "scr_diagram"),
                help="output path without extension; writes .png and .pdf")
args = ap.parse_args()
for ext in ("png", "pdf"):
    fig.savefig(f"{args.out}.{ext}", dpi=170, facecolor="white")
print(f"wrote {args.out}.png and .pdf")
