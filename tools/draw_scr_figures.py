"""
Two figures of the SCR system, in tools/:
  scr_pipeline      how the project works: map the room before the exam, then track the probe
                    during it (classical SIFT odometry + SCR anchors + pose graph -> pose of every
                    US image); colours: blue sensors and data, purple learned, green training,
                    orange geometry (no learning), white result
  scr_architecture  the SCR anchor in paper style (one column of a two-column page, 7.4 x 2.75 in):
                    image encoder, coordinate head, scene coordinates, geometric pose solver, with
                    tensor shapes and real thumbnails of one sweep frame (RGB, depth, and the
                    room-coordinate labels of its 45 x 80 cells); flame = trained on the room scan

  python tools/draw_scr_figures.py                 # -> tools/scr_pipeline.png/.pdf, tools/scr_architecture.png/.pdf
  python tools/draw_scr_figures.py --root $DATA/train_3XX --run run-316 --row 400

No result numbers in the figures (they are in summary.md).
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

INK, MUTED, RULE = "#1f1f1e", "#5f5e58", "#c9c8c0"
NET = ("#ece9fb", "#5b47c7")
TRAIN = ("#dff4ea", "#178a5e")
GEO = ("#fff2dc", "#b8770b")
DATA = ("#e3eefb", "#2f6db5")
OUT = ("#ffffff", "#1f1f1e")


def canvas(w, h, xl, yl):
    fig = plt.figure(figsize=(w, h), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, xl)
    ax.set_ylim(0, yl)
    ax.axis("off")
    return fig, ax


def box(ax, x, y, w, h, title, sub="", style=NET, dashed=False, fs=11, sfs=8.6):
    fill, edge = style
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.25,rounding_size=1.0",
                                fc=fill, ec=edge, lw=1.6, ls="--" if dashed else "-"))
    if not sub:
        ax.text(x + w / 2, y + h / 2, title, ha="center", va="center", fontsize=fs, color=INK, weight="bold")
        return
    n, nt = sub.count("\n") + 1, title.count("\n") + 1
    block = 1.55 + 1.9 * (nt - 1) + 0.98 * n * sfs / 8.6
    top = y + h / 2 + block / 2 + 0.35
    ax.text(x + w / 2, top, title, ha="center", va="top", fontsize=fs, color=INK, weight="bold", linespacing=1.2)
    ax.text(x + w / 2, top - 1.75 - 1.9 * (nt - 1), sub, ha="center", va="top", fontsize=sfs, color=MUTED,
            linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=MUTED, dashed=False, label=None, lx=0.0, ly=0.0, rad=0.0):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=12, color=color, lw=1.35,
                                 ls="--" if dashed else "-", connectionstyle=f"arc3,rad={rad}"))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontsize=8.3, color=color, ha="center", va="center",
                bbox=dict(fc="white", ec="none", pad=0.6))


def legend(ax, x, y, items, step=24):
    for i, (style, lab) in enumerate(items):
        xx = x + i * step
        ax.add_patch(FancyBboxPatch((xx, y), 3, 1.8, boxstyle="round,pad=0.1", fc=style[0], ec=style[1], lw=1.4))
        ax.text(xx + 4, y + 0.9, lab, fontsize=8.8, va="center", color=INK)


def band(ax, y0, y1, label, xl):
    ax.add_patch(FancyBboxPatch((0.8, y0), xl - 1.6, y1 - y0, boxstyle="round,pad=0,rounding_size=1.5",
                                fc="#f7f7f4", ec="none"))
    ax.text(2.2, y1 - 1.6, label, fontsize=12.5, weight="bold", color=INK, va="top")


# ---------------------------------------------------------------- 1. pipeline
def pipeline():
    fig, ax = canvas(16, 8.6, 160, 86)
    ax.text(2, 83.2, "Markerless probe tracking with scene coordinate regression (SCR) anchors", fontsize=15.5,
            weight="bold", color=INK)
    ax.text(2, 79.8, "one RGB-D camera on the ultrasound probe; nothing outside the probe during the exam",
            fontsize=10, color=MUTED)

    # A. before the exam
    band(ax, 50, 77, "A   Before the exam: map the room (once per room / session)", 160)
    box(ax, 4, 54, 34, 15, "Room scan", "move the probe camera around\nthe room for 1-3 min\nRGB + depth video", DATA)
    box(ax, 50, 54, 34, 15, "Room-scan poses", "camera pose of every scan frame\n(here: Polaris; in deployment:\nSLAM from the scan itself)", DATA)
    box(ax, 96, 54, 34, 15, "Train the SCR network", "learns the room coordinate of\nevery image cell, from depth\n(one GPU, 25-50 min)", TRAIN)
    box(ax, 140, 56.5, 17, 10, "Room model", "SCR network\nweights", NET, fs=10.5, sfs=8.4)
    arrow(ax, 38.4, 61.5, 49.6, 61.5)
    arrow(ax, 84.4, 61.5, 95.6, 61.5)
    arrow(ax, 130.4, 61.5, 139.6, 61.5)

    # B. during the exam
    band(ax, 4, 47, "B   During the exam: track the probe, no tracker", 160)
    box(ax, 4, 12, 26, 27, "Probe", "RGB-D camera (D435i)\n+ ultrasound probe\n\nRGB, depth, US image\n~30 frames/s", DATA)
    box(ax, 42, 27, 36, 14.5, "SCR anchor (every 1 s)", "SCR network -> room coordinate per cell\n+ measured depth -> Kabsch RANSAC\n"
        "-> absolute camera pose in the room\n(the only anchors; no features)", NET)
    box(ax, 42, 10, 36, 11.5, "Odometry", "camera motion between frames 0.27 s apart\nSIFT features + depth, PnP-RANSAC\n(classical, not learned); drifts", GEO)
    box(ax, 90, 18, 26, 14, "Pose graph", "anchors remove drift,\nodometry fills the gaps\n-> camera pose\nof every frame", GEO)
    box(ax, 128, 25, 29, 13, "Pose of every\nUS image", "camera pose x hand-eye\nx US calibration", GEO, sfs=8.4)
    box(ax, 128, 8, 29, 12.5, "3D ultrasound volume", "US images placed in the room\nand compounded", OUT)
    arrow(ax, 30.4, 34.2, 41.6, 34.2)
    arrow(ax, 30.4, 15.8, 41.6, 15.8)
    arrow(ax, 78.4, 34.2, 89.6, 27.5)
    arrow(ax, 78.4, 15.8, 89.6, 22.5)
    arrow(ax, 116.4, 25.0, 127.6, 30.5)
    arrow(ax, 142.5, 24.6, 142.5, 20.9)
    # the room model feeds the anchors
    ax.plot([148.5, 148.5, 60], [56.1, 49.5, 49.5], color=NET[1], lw=1.35)
    arrow(ax, 60, 49.5, 60, 41.9, color=NET[1])
    ax.text(104, 50.6, "room model", fontsize=8.6, color=NET[1], ha="center")

    # evaluation note
    ax.text(4, 5.2, "Evaluation (not part of the system): a Polaris marker on the probe gives the true pose; errors are "
            "measured at the US image, ~16 cm from the camera, where 1 degree of rotation is ~1.6 mm.",
            fontsize=9, color=MUTED)
    legend(ax, 4, 0.8, [(DATA, "sensors and data"), (NET, "learned"), (TRAIN, "training"), (GEO, "geometry, no learning"),
                        (OUT, "result")])
    return fig


# ---------------------------------------------------------------- 2. architecture (paper style)
P_ENC = ("#e6f0f7", "#6f93ad")      # encoder panel
P_HEAD = ("#f4e9f6", "#a07aae")     # head panel
P_SOLV = ("#eaf4e6", "#7da36e")     # solver panel
SUB = ("#ffffff", "#9a9a9a")        # inner boxes
CELL_A, CELL_B, CELL_C = "#9fb7d6", "#c7a6d1", "#a9c79b"


def thumbnails(root, run, row):
    """RGB, depth and the room-coordinate labels of the 45 x 80 cells of one sweep frame, or None."""
    try:
        import cv2
        import numpy as np
        import sys
        repo = Path(__file__).resolve().parents[1]
        sys.path.insert(0, str(repo))
        from dataloader import RPRConfig, RPRDataset, load_hand_eye
        ds = RPRDataset(root, [run], [], RPRConfig(T_marker_cam=load_hand_eye(str(repo / "T_marker_cam.npy"), "mm")))
        r = ds.runs[run]
        rows = np.concatenate(r["segments"])
        row = int(rows[len(rows) // 2] if row is None else row)
        rgb = cv2.cvtColor(cv2.imread(str(Path(root) / run / r["df"]["rgb"].iloc[row])), cv2.COLOR_BGR2RGB)
        depth = cv2.imread(str(Path(root) / run / r["df"]["depth"].iloc[row]), cv2.IMREAD_UNCHANGED) * r["depth_scale"]
        K, T = np.asarray(r["K"], float), r["T_world_cam"][row]
        v, u = np.mgrid[0:45, 0:80] * 16 + 8                                 # cell centres, full resolution
        z = depth[v, u].astype(float)
        X = np.stack([(u - K[0, 2]) / K[0, 0] * z, (v - K[1, 2]) / K[1, 1] * z, z, np.ones_like(z)], -1) @ T.T
        ok = (z > 100) & (z < 2000)
        lo, hi = (np.percentile(X[..., :3][ok], q, axis=0) for q in (2, 98))
        coord = np.clip((X[..., :3] - lo) / (hi - lo), 0, 1)
        coord[~ok] = 1.0
        dview = np.clip((depth - 200) / 2300, 0, 1)
        dview[depth == 0] = np.nan
        return rgb, dview, coord
    except Exception as e:                                                     # no data here: grey placeholders
        print(f"thumbnails: {type(e).__name__}: {e}; drawing placeholders")
        return None


def architecture(thumbs=None):
    plt.rcParams["font.family"] = "Nimbus Sans"
    fig, ax = canvas(7.4, 2.75, 185, 68.75)

    def panel(x, y, w, h, title, style):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.6", fc=style[0], ec=style[1], lw=0.9))
        ax.text(x + w / 2, y + h + 1.4, title, ha="center", va="bottom", fontsize=7.4, weight="bold", color=INK)

    def sub(x, y, w, h, text, fs=5.6, style=SUB, dashed=False, weight="normal"):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=1.0", fc=style[0], ec=style[1],
                                    lw=0.7, ls="--" if dashed else "-"))
        if text:
            ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=INK, linespacing=1.25,
                    weight=weight)

    def arr(x1, y1, x2, y2, color="#2b2b2b", dashed=False, lw=0.7):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=6, color=color, lw=lw,
                                     ls="--" if dashed else "-", shrinkA=0, shrinkB=0))

    def cells(x, y, n, color, s=1.7, gap=0.6, vertical=False):
        for i in range(n):
            xx, yy = (x, y - i * (s + gap)) if vertical else (x + i * (s + gap), y)
            ax.add_patch(plt.Rectangle((xx, yy), s, s, fc=color, ec="#555555", lw=0.35))

    def flame(x, y, s=1.0):
        import numpy as np
        t = np.linspace(0, 2 * np.pi, 60)
        for sc, col in ((1.0, "#e8432e"), (0.55, "#f6b13c")):
            px = x + s * sc * 1.05 * np.sin(t) * (1 - 0.25 * np.cos(t))
            py = y + s * sc * (1.3 * (1 - np.cos(t)) / 2 * 1.4 - 0.2) * 1.25
            ax.fill(px, py, color=col, lw=0)

    def image(img, x, y, w, h, cmap=None, nearest=False):
        if img is None:
            ax.add_patch(plt.Rectangle((x, y), w, h, fc="#d9d9d9", ec="#777777", lw=0.4))
            return
        ax.imshow(img, extent=(x, x + w, y, y + h), cmap=cmap, interpolation="nearest" if nearest else "bilinear",
                  aspect="auto", zorder=2)
        ax.add_patch(plt.Rectangle((x, y), w, h, fc="none", ec="#555555", lw=0.4, zorder=3))

    rgb, dep, coord = thumbs if thumbs else (None, None, None)

    # inputs
    ax.text(10.5, 60.2, "RGB frame", ha="center", fontsize=6.4, color=INK)
    image(rgb, 2, 49.5, 17, 9.6)
    ax.text(10.5, 46.9, "3 × 360 × 640", ha="center", fontsize=5.4, color=MUTED)
    ax.text(10.5, 22.2, "Depth (aligned)", ha="center", fontsize=6.4, color=INK)
    image(dep, 2, 11.5, 17, 9.6, cmap="viridis")
    ax.text(10.5, 8.9, "1 × 720 × 1280, mm", ha="center", fontsize=5.4, color=MUTED)

    # 1. encoder
    panel(23, 6, 54, 54, "Image Encoder", P_ENC)
    sub(25.5, 30, 15, 23, "EfficientNet-B0\n\nImageNet init.\nfine-tuned\n(lr 1e-4)", fs=5.6)
    flame(38.4, 49.8, 0.9)
    arr(19.4, 54.3, 25.3, 43)
    sub(43.5, 9, 31, 47, "", fs=5.6)
    ax.text(59, 53.4, "Two-scale fusion", ha="center", fontsize=6.0, color=INK)
    ax.text(44.6, 49.3, "stride 8", fontsize=5.2, color=INK)
    cells(51.8, 47.2, 4, CELL_A)
    ax.text(45, 44.6, "40 × 45 × 80", fontsize=4.8, color=MUTED)
    ax.text(44.6, 39.4, "stride 16", fontsize=5.2, color=INK)
    cells(51.8, 37.2, 4, CELL_B)
    ax.text(45, 34.6, "112 × 23 × 40", fontsize=4.8, color=MUTED)
    ax.text(45, 31.2, "bilinear ×2", fontsize=4.8, color=MUTED, style="italic")
    arr(40.9, 47.9, 51.3, 47.9)
    arr(40.9, 38.0, 51.3, 38.0)
    ax.text(66.5, 42.9, r"$\oplus$", ha="center", va="center", fontsize=10, color=INK)
    arr(61.3, 48.0, 65.2, 44.3)
    arr(61.3, 38.0, 65.2, 41.5)
    cells(71.2, 47.8, 5, "#b6b0d8", s=1.5, gap=0.5, vertical=True)
    arr(68.5, 42.9, 70.9, 42.9)
    ax.text(59, 24.0, "concatenate per cell\n152 × 45 × 80", ha="center", fontsize=5.0, color=MUTED, linespacing=1.25)
    ax.text(59, 13.5, "ImageNet features: fine detail (stride 8)\n+ wider context (stride 16)", ha="center",
            fontsize=4.8, color=MUTED, linespacing=1.25)

    # 2. coordinate head
    panel(81, 6, 37, 54, "Coordinate Head", P_HEAD)
    flame(114.6, 55.0, 0.9)
    x0, yc = 84.2, 39
    for i, (h, lab) in enumerate([(21, "152→512"), (16, ""), (16, ""), (16, ""), (16, ""), (8, "512→3")]):
        xx = x0 + i * 5.1
        col = "#d8c3e0" if i in (0, 5) else "#e9dcef"
        ax.add_patch(FancyBboxPatch((xx, yc - h / 2), 3.0, h, boxstyle="round,pad=0,rounding_size=1.2", fc=col,
                                    ec="#8a6a98", lw=0.6))
        if i:
            arr(xx - 2.0, yc, xx - 0.1, yc, lw=0.5)
    for i in range(1, 5):                                                      # residual skips
        xx = x0 + i * 5.1 + 1.5
        ax.add_patch(FancyArrowPatch((xx - 2.6, yc + 8.6), (xx + 2.4, yc + 8.6), connectionstyle="arc3,rad=-0.9",
                                     arrowstyle="-|>", mutation_scale=4, color="#8a6a98", lw=0.45))
    ax.text(99.5, 22.0, "1×1 convolutions: every cell regressed on its own\n"
            "4 residual blocks (width 512), ReLU, fp32\n2.18 M parameters (lr 1e-3)", ha="center", fontsize=4.8,
            color=MUTED, linespacing=1.3)
    ax.text(85.7, 50.8, "152→512", fontsize=4.6, color=MUTED)
    ax.text(111.2, 32.6, "512→3", fontsize=4.6, color=MUTED, ha="center")
    arr(74.6, 42.9, 84.0, 41.0)
    sub(83.5, 9, 32, 7.5, "labels: depth + room-scan pose\n" r"loss: mean $\Vert\hat{y} - y\Vert_2$ (3D, m)", fs=4.8,
        style=("#ffffff", "#178a5e"), dashed=True)

    # scene coordinates (output of the network)
    ax.text(130.5, 60.2, "Scene coordinates", ha="center", fontsize=6.4, color=INK)
    image(coord, 122, 49.5, 17, 9.6, nearest=True)
    ax.text(130.5, 46.9, "3 × 45 × 80: room (x, y, z)", ha="center", fontsize=5.2, color=MUTED)
    arr(114.0, 39.0, 121.6, 51.5)

    # 3. pose solver
    panel(143, 6, 40, 54, "Geometric Pose Solver", P_SOLV)
    sub(145.5, 43, 35, 13.5, "", fs=5.4)
    ax.text(163, 53.6, "3D–3D correspondences", ha="center", fontsize=5.6, color=INK)
    import numpy as np
    rng = np.random.default_rng(3)
    for k in range(6):                                                         # C (camera) <-> P (room) pairs
        yy = 46.6 + k * 1.0
        bad = k in (2, 5)
        ax.plot([150.5, 175.5], [yy, yy + rng.uniform(-0.4, 0.4)], color="#c94c4c" if bad else "#6d8f60",
                lw=0.45, ls=":" if bad else "-")
        ax.add_patch(plt.Circle((150.5, yy), 0.45, fc="#9fb7d6", ec="none"))
        ax.add_patch(plt.Circle((175.5, yy), 0.45, fc="#b6b0d8", ec="none"))
    ax.text(148.9, 49.1, r"$C$", fontsize=5.6, color=INK, ha="right", va="center")
    ax.text(177.1, 49.1, r"$\hat{P}$", fontsize=5.6, color=INK, ha="left", va="center")
    ax.text(163, 44.4, r"$C$: back-projected depth    $\hat{P}$: network", ha="center", fontsize=4.6, color=MUTED)
    sub(145.5, 26.5, 21.5, 11.5, "Kabsch RANSAC\n256 hypotheses\ninlier < 20 mm\n3 refits", fs=5.0)
    sub(145.5, 11, 21.5, 11.5, "Inlier gate\n≥ 400 inliers\n(recovery after\n3 agreeing anchors)", fs=5.0)
    arr(156.2, 42.8, 156.2, 38.3)
    arr(156.2, 26.3, 156.2, 22.8)
    for k in range(3):                                                          # 6-DoF output, R and t
        ax.add_patch(plt.Circle((173.0, 34.8 - k * 2.6), 1.0, fc="#f2c9c3", ec="#b07a73", lw=0.5))
        ax.add_patch(plt.Circle((177.6, 34.8 - k * 2.6), 1.0, fc="#d9d2ee", ec="#7f73a6", lw=0.5))
    ax.text(173.0, 37.6, "R", ha="center", fontsize=5.4, color=INK)
    ax.text(177.6, 37.6, "t", ha="center", fontsize=5.4, color=INK)
    ax.text(175.3, 26.6, "anchor\n" r"$T_\mathrm{world,cam}$" "\n" r"$\in SE(3)$", ha="center", va="top", fontsize=5.0,
            color=INK, linespacing=1.4)
    arr(167.2, 32.0, 171.6, 32.0)
    ax.text(175.3, 13.5, "no learning", ha="center", fontsize=4.8, color=MUTED, style="italic")
    arr(139.4, 52.0, 145.3, 49.5)

    # depth: labels (training, dashed) and camera points (use)
    ax.plot([19.4, 21.2, 21.2], [16.3, 16.3, 3.2], color="#2b2b2b", lw=0.6)
    ax.plot([21.2, 184], [3.2, 3.2], color="#2b2b2b", lw=0.6)
    ax.plot([184, 184], [3.2, 49.6], color="#2b2b2b", lw=0.6)
    arr(184, 49.6, 180.7, 49.6)
    ax.plot([99.5, 99.5], [3.2, 8.8], color="#178a5e", lw=0.6, ls="--")
    ax.text(140, 4.0, "depth at the cell centres", fontsize=4.8, color=MUTED, ha="center", va="bottom")

    # legend
    flame(122.4, 19.0, 0.75)
    ax.text(124.6, 20.0, "trained on the\nroom scan", fontsize=5.0, color=MUTED, va="center", linespacing=1.2)
    ax.plot([121.2, 123.8], [13.6, 13.6], color="#178a5e", lw=0.7, ls="--")
    ax.text(124.6, 13.6, "training only", fontsize=5.0, color=MUTED, va="center")
    plt.rcParams["font.family"] = "DejaVu Sans"
    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent))
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2] / "rgbd-us" / "data" / "train_3XX"),
                    help="collection with the sweep for the image thumbnails (grey boxes if missing)")
    ap.add_argument("--run", default="run-316")
    ap.add_argument("--row", type=int, default=None, help="frame (default: middle of the sweep)")
    args = ap.parse_args()
    thumbs = thumbnails(args.root, args.run, args.row)
    for name, make in (("scr_pipeline", pipeline), ("scr_architecture", lambda: architecture(thumbs))):
        fig = make()
        for ext in ("png", "pdf"):
            fig.savefig(Path(args.out_dir) / f"{name}.{ext}", dpi=170 if name == "scr_pipeline" else 400, facecolor="white")
        plt.close(fig)
        print(f"wrote {Path(args.out_dir) / name}.png and .pdf")


if __name__ == "__main__":
    main()
