"""
Draw the model diagram: RPRNet (one architecture, trained twice as odometry and as anchor
network) and how the two trained copies are combined into one trajectory.

  python tools/draw_diagram.py                 # -> model_diagram.png and .pdf in the repo root
  python tools/draw_diagram.py --out figures/model_diagram

Colours: purple = both networks (right panel: the odometry path), green = anchor network only,
grey dashed = optional and off in the reported runs (US, dt), orange = arithmetic, no learning.
The numbers in the last box (12.3 / 33.8 mm) are the 8-fold results of 5 Oct 2026; update them
when the results change.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

INK, MUTED, RULE = "#1f1f1e", "#6b6a64", "#c9c8c0"
BOTH = ("#ece9fb", "#5b47c7")       # fill, edge: used by both networks
ANCH = ("#dff4ea", "#178a5e")       # anchor network only
OPT = ("#f4f4f1", "#9a998f")        # optional, off in the reported runs
POST = ("#fff2dc", "#b8770b")       # arithmetic, no learning
OUT = ("#ffffff", "#1f1f1e")        # result

fig = plt.figure(figsize=(16, 9.8), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, 160)
ax.set_ylim(0, 96)
ax.axis("off")


def box(x, y, w, h, title, sub="", style=BOTH, dashed=False, fs=11):
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


# ---------------- left: the network ----------------
ax.text(2, 93, "RPRNet: one architecture, trained twice", fontsize=15, weight="bold", color=INK)
ax.text(2, 89.6, "relative pose of frame B with respect to frame A,  xi = [translation mm | rotation rad]",
        fontsize=9.5, color=MUTED)

box(2, 76, 28, 8, "RGB frames A, B", "odometry: frames k, k+4\nanchor: keyframe, frame t")
box(34, 76, 24, 8, "Depth + valid mask", "anchor network only", ANCH)
box(62, 76, 20, 8, "US frames", "optional (--use-us), off", OPT, dashed=True)

box(2, 62, 28, 8, "RGB encoder, shared", "EfficientNet-B0 stages 1-4, stride 8\nodometry: fine-tuned | anchor: frozen")
box(34, 62, 24, 8, "Depth stem", "3 convs, stride 8", ANCH)
box(62, 62, 20, 8, "US encoder", "small CNN, one vector per frame", OPT, dashed=True)
for x in (16, 46, 72):
    arrow(x, 76, x, 70.4, dashed=(x == 72))

box(2, 49, 56, 8, "Fuse per frame", "concat + 1x1 conv (64 ch), stride 8")
arrow(16, 62, 16, 57.4)
arrow(46, 62, 46, 57.4, color=ANCH[1])

box(2, 34, 34, 10, "Pair features", "f_A, f_B, f_B - f_A,\nfine correlation (+-3 cells, stride 8)")
box(40, 34, 18, 10, "Coarse correlation", "stride 32, +-128 px\nanchor only", ANCH)
arrow(19, 49, 19, 44.4)
arrow(49, 49, 49, 44.4, color=ANCH[1])

box(2, 20, 56, 8, "Motion convs + global pooling", "stride 8 -> 32, 256 features")
arrow(19, 34, 19, 28.4)
arrow(49, 34, 40, 28.4, color=ANCH[1])

box(2, 6, 56, 10, "Pose head (MLP)", "-> xi (6 numbers) per pair; last layer small random init\n+ US vectors x us_valid, + time gap dt (both optional, off)")
arrow(30, 20, 30, 16.4)
arrow(72, 62, 72, 12, dashed=True)
arrow(72, 12, 58.4, 12, dashed=True)
ax.text(64, 30, "dt (--use-dt, off)", fontsize=8.5, color=OPT[1], ha="center")
arrow(64, 28.5, 58.4, 13.5, color=OPT[1], dashed=True)

# legend
lx, ly = 2, 1.2
for i, (style, lab, d) in enumerate([(BOTH, "both networks (right: odometry)", False), (ANCH, "anchor network only", False),
                                     (OPT, "optional, off in reported runs", True), (POST, "arithmetic, no learning", False)]):
    xx = lx + i * 27
    ax.add_patch(FancyBboxPatch((xx, ly), 3, 2.2, boxstyle="round,pad=0.1", fc=style[0], ec=style[1],
                                lw=1.4, ls="--" if d else "-"))
    ax.text(xx + 4, ly + 1.1, lab, fontsize=8.8, va="center", color=INK)

# divider
ax.plot([88, 88], [4, 92], color=RULE, lw=1)

# ---------------- right: how the two networks are used ----------------
ax.text(92, 93, "Two trained copies, one trajectory", fontsize=15, weight="bold", color=INK)
ax.text(92, 89.6, "separate weights: runs/rpr-rgb-gap4 (odometry), runs/anchor-rgbd-v2-reg (anchor)",
        fontsize=9.5, color=MUTED)

box(92, 71, 31, 13, "Odometry network", "RGB, frames k and k+4 (~133 ms)\nencoder fine-tuned\nevery step (~7.5 / s): ~1 mm motion", fs=11.5)
box(127, 71, 31, 13, "Anchor network", "RGB-D, room-scan keyframe + frame\nencoder frozen, + depth, + coarse corr.\n~1 / s: 7-17 cm offset", ANCH, fs=11.5)

box(92, 54, 31, 10, "Chain the steps", "pose(k+4) = pose(k) x step\nprecise short term, drifts", POST)
box(127, 54, 31, 10, "Absolute pose", "keyframe pose x predicted offset\n3 keyframes averaged, 50 mm gate", POST)
arrow(107.5, 71, 107.5, 64.4)
arrow(142.5, 71, 142.5, 64.4, color=ANCH[1])

box(127, 41, 31, 8, "Keyframe retrieval", "nearest room-scan keyframes\nto the current odometry pose", POST)
arrow(123, 57, 127, 45, color=POST[1])
ax.text(118.5, 49.5, "pose", fontsize=8.5, color=POST[1])
arrow(142.5, 49, 142.5, 53.6, color=POST[1])

box(92, 24, 66, 11, "Combine", "live: reset the pose at each accepted anchor\n"
    "offline: pose graph, fits the whole path to odometry steps + anchors", POST, fs=11.5)
arrow(107.5, 54, 107.5, 35.4)
arrow(142.5, 41, 142.5, 35.4, color=POST[1])

box(92, 8, 66, 10, "Pose of every US frame",
    "-> US volume (stacked images)\n12.3 mm at the US image (offline, 8 held-out sweeps; odometry alone 33.8 mm)", OUT, fs=11.5)
arrow(125, 24, 125, 18.4)

ap = argparse.ArgumentParser()
ap.add_argument("--out", default=str(Path(__file__).resolve().parent.parent / "model_diagram"),
                help="output path without extension; writes .png and .pdf")
args = ap.parse_args()
for ext in ("png", "pdf"):
    fig.savefig(f"{args.out}.{ext}", dpi=170, facecolor="white")
print(f"wrote {args.out}.png and .pdf")
