"""
Two figures of the SCR system, in tools/:
  scr_pipeline      how the project works: map the room before the exam (the network builds its own
                    room-scan poses, scr_map.py), then track the probe
                    during it with the SCR network alone (every frame, Kabsch RANSAC, temporal
                    smoothing -> pose of every US image; summary 3.1); colours: blue sensors and data, purple learned, green training,
                    orange geometry (no learning), white result
  scr_architecture  the network in paper style (full page width, 7.4 x 5.0 in; style of Recon2Servo /
                    MagServo), two stages: I room-scan training in detail (inputs, photometric
                    augmentation, encoder + head with tensor shapes, label generation and mask, the
                    loss L_coord and the optimiser); II tracking during the exam (frozen network, dense
                    3D-3D pairs from the cell grid, Kabsch RANSAC, temporal smoothing, US image pose).
                    Thumbnails: one sweep frame (RGB, depth, room-coordinate labels of its 45 x 80 cells);
                    flame = trainable, snowflake = frozen
  scr_mapping       how the room-scan poses (the training labels) are made without a tracker (scr_map.py):
                    seed by depth ICP, rounds of train / localise / extend, final pass, pose graph, labels;
                    Polaris only to evaluate (alignment + camera calibration)

  python tools/draw_scr_figures.py                 # -> tools/scr_pipeline, scr_architecture, scr_mapping (.png/.pdf)
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
    ax.text(2, 83.2, "Markerless probe tracking with one scene coordinate regression (SCR) network", fontsize=15.5,
            weight="bold", color=INK)
    ax.text(2, 79.8, "one RGB-D camera on the ultrasound probe, one network, no odometry, no tracker: the network also "
            "builds its own training labels", fontsize=10, color=MUTED)

    # A. before the exam
    band(ax, 50, 77, "A   Before the exam: map the room (once per room / session)", 160)
    box(ax, 4, 54, 27, 15, "Room scan", "move the probe camera\naround the room, 1-3 min\nRGB + depth video", DATA)
    box(ax, 38, 53, 46, 17, "Self-mapping (no tracker)", "the SCR network + depth ICP give the\npose of every scan frame;"
        " a pose graph\nties neighbouring frames together\n(scr_map.py; benchmark runs: Polaris)", NET, sfs=8.3)
    box(ax, 91, 54, 40, 15, "Train the SCR network", "on those poses: the room coordinate\nof every image cell, from depth\n(one GPU, 25-50 min)", TRAIN)
    box(ax, 140, 56.5, 17, 10, "Room model", "SCR network\nweights", NET, fs=10.5, sfs=8.4)
    arrow(ax, 31.4, 61.5, 37.6, 61.5)
    arrow(ax, 84.4, 61.5, 90.6, 61.5)
    arrow(ax, 131.4, 61.5, 139.6, 61.5)

    # B. during the exam
    band(ax, 4, 47, "B   During the exam: track the probe with the network alone", 160)
    box(ax, 4, 15, 24, 25, "Probe", "RGB-D camera (D435i)\n+ ultrasound probe\n\nRGB, depth, US image\n~30 frames/s", DATA)
    box(ax, 35, 23, 28, 15, "SCR network", "every frame:\nroom coordinate of\nevery image cell", NET)
    box(ax, 70, 23, 26, 15, "Kabsch RANSAC", "+ measured depth\n-> camera pose in the room\n(dropped if < 400 inliers)", GEO)
    box(ax, 103, 23, 22, 15, "Temporal\nsmoothing", "robust local fit\nover +-1 s", GEO, sfs=8.4)
    box(ax, 131, 26, 26, 12, "Pose of every\nUS image", "camera pose x camera-to-US\ncalibration (once per probe)", GEO, sfs=8.0)
    box(ax, 131, 8, 26, 12, "3D ultrasound volume", "US images placed in the\nroom and compounded", OUT, sfs=8.4)
    arrow(ax, 28.4, 32, 34.6, 32, label="RGB", ly=1.3)
    arrow(ax, 63.4, 30.5, 69.6, 30.5)
    arrow(ax, 96.4, 30.5, 102.6, 30.5)
    arrow(ax, 125.4, 30.5, 130.6, 31.5)
    arrow(ax, 144, 25.6, 144, 20.4)
    ax.plot([28.4, 32, 32, 83], [19, 19, 17.6, 17.6], color=MUTED, lw=1.35)               # depth -> Kabsch
    arrow(ax, 83, 17.6, 83, 22.6)
    ax.text(57, 18.8, "depth", fontsize=8.3, color=MUTED, ha="center")
    ax.plot([16, 16, 120], [14.6, 11.5, 11.5], color=MUTED, lw=1.35)                       # US images -> volume
    arrow(ax, 120, 11.5, 130.6, 11.5)
    ax.text(70, 12.6, "US images", fontsize=8.3, color=MUTED, ha="center")
    # the room model feeds the network
    ax.plot([148.5, 148.5, 49], [56.1, 49.5, 49.5], color=NET[1], lw=1.35)
    arrow(ax, 49, 49.5, 49, 38.4, color=NET[1])
    ax.text(100, 50.6, "room model", fontsize=8.6, color=NET[1], ha="center")

    # evaluation note
    ax.text(4, 5.2, "Evaluation only: a Polaris marker on the probe gives the true pose; errors at the US image (~16 cm "
            "from the camera, 1 degree ~ 1.6 mm). Polaris also gives the probe's camera-to-US calibration once.",
            fontsize=8.8, color=MUTED)
    legend(ax, 4, 0.8, [(DATA, "sensors and data"), (NET, "learned"), (TRAIN, "training"), (GEO, "geometry, no learning"),
                        (OUT, "result")])
    return fig


# ---------------------------------------------------------------- 3. mapping without a tracker
def mapping():
    fig, ax = canvas(16, 7.8, 160, 78)
    ax.text(2, 75.2, "Mapping without a tracker: the SCR network makes its own training labels (scr_map.py)", fontsize=15.5,
            weight="bold", color=INK)
    ax.text(2, 71.8, "input: the room-scan RGB-D video only; no Polaris, no SLAM system, no keypoints. Output: the camera "
            "pose of every scan frame, the labels of Stage I", fontsize=10, color=MUTED)

    band(ax, 38, 69, "A   Grow the map (ACE0-style, with the measured depth)", 160)
    box(ax, 4, 44, 22, 16, "Room scan", "RGB + depth video\n1-3 min, 30 frames/s", DATA)
    box(ax, 32, 44, 26, 16, "1  Seed", "one frame = map origin;\nthe 2 s around it joined\nby frame-to-frame\ndepth ICP", GEO)
    box(ax, 66, 44, 26, 16, "2a  Train", "the network on the\nframes mapped so far\n(labels from their poses,\nL_coord, 1,500 steps)", TRAIN)
    box(ax, 99, 44, 27, 16, "2b  Localise", "unmapped neighbours:\nKabsch RANSAC >= 60 inliers\n+ plausible motion;\nfar frames >= 400", NET)
    box(ax, 133, 44, 24, 16, "2c  Extend", "each map edge\nby depth ICP\n(up to 90 frames)", GEO)
    arrow(ax, 26.4, 52, 31.6, 52)
    arrow(ax, 58.4, 52, 65.6, 52)
    arrow(ax, 92.4, 52, 98.6, 52)
    arrow(ax, 126.4, 52, 132.6, 52)
    arrow(ax, 145, 43.6, 79, 43.6, rad=-0.18, label="next round, until a round adds < 0.5 % of the frames", ly=-1.2)

    band(ax, 6, 35, "B   Refine and hand over", 160)
    box(ax, 4, 11, 30, 16, "3  Final pass", "every frame localised\nagain by the last network\n(>= 400 inliers)", NET)
    box(ax, 41, 9, 44, 20, "4  Pose graph", "depth-ICP edges between frames\n1, 5, 15, 30 apart (1 mm)\n+ each frame's network pose as a\n"
        "prior on the points 1 m ahead (10 mm)\nrobust least squares", GEO, sfs=8.3)
    box(ax, 92, 11, 30, 16, "5  Labels", "pose of every scan frame\n-> train the final network\n(Stage I, 120 epochs)", TRAIN)
    box(ax, 129, 11, 28, 16, "Evaluation only", "Polaris: one rigid alignment\n+ camera-to-US calibration\n(once per probe)", DATA,
        dashed=True, sfs=8.3)
    arrow(ax, 34.4, 19, 40.6, 19)
    arrow(ax, 85.4, 19, 91.6, 19)
    arrow(ax, 122.4, 19, 128.6, 19, dashed=True)
    ax.plot([157.5, 158.6, 158.6, 31, 31], [52, 52, 36.5, 36.5, 28.5], color=MUTED, lw=1.35)
    arrow(ax, 31, 28.6, 31, 27.4)
    ax.text(95, 36.5, "map complete", fontsize=8.3, color=MUTED, ha="center", va="center", bbox=dict(fc="white", ec="none", pad=0.6))
    legend(ax, 4, 1.6, [(DATA, "data"), (NET, "network (inference)"), (TRAIN, "network training"),
                        (GEO, "geometry, no learning")], step=30)
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
    """Paper-style figure in two stages (as Recon2Servo / MagServo): I training on the room scans (detail,
    with the loss), II tracking during the exam (network frozen). Flame = trainable, snowflake = frozen."""
    import numpy as np
    from matplotlib.patches import Polygon
    plt.rcParams["font.family"] = "Nimbus Sans"
    plt.rcParams["mathtext.fontset"] = "dejavusans"
    fig, ax = canvas(7.4, 5.0, 185, 125)
    STAGE1 = ("#eaf5ee", "#7fb08f")
    STAGE2 = ("#fbf1e6", "#d1a46f")
    LOSS = ("#fff5f4", "#c0504d")

    def rbox(x, y, w, h, style, lw=0.7, dashed=False, r=1.2):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=style[0], ec=style[1],
                                    lw=lw, ls="--" if dashed else "-"))

    def txt(x, y, t, fs=4.8, color=INK, ha="center", va="center", **kw):
        ax.text(x, y, t, fontsize=fs, color=color, ha=ha, va=va, linespacing=1.32, **kw)

    def arr(x1, y1, x2, y2, color="#2b2b2b", dashed=False, lw=0.7, rad=0.0):
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=6, color=color, lw=lw,
                                     ls="--" if dashed else "-", shrinkA=0, shrinkB=0,
                                     connectionstyle=f"arc3,rad={rad}"))

    def cells(x, y, n, color, s=1.7, gap=0.6, vertical=False):
        for i in range(n):
            xx, yy = (x, y - i * (s + gap)) if vertical else (x + i * (s + gap), y)
            ax.add_patch(plt.Rectangle((xx, yy), s, s, fc=color, ec="#555555", lw=0.35))

    def flame(x, y, s=0.8):
        t = np.linspace(0, 2 * np.pi, 60)
        for sc, col in ((1.0, "#e8432e"), (0.55, "#f6b13c")):
            px = x + s * sc * 1.05 * np.sin(t) * (1 - 0.25 * np.cos(t))
            py = y + s * sc * (1.3 * (1 - np.cos(t)) / 2 * 1.4 - 0.2) * 1.25
            ax.fill(px, py, color=col, lw=0, zorder=5)

    def snow(x, y, s=1.3):
        for a in (0, 60, 120):
            dx, dy = s * np.cos(np.radians(a)), s * np.sin(np.radians(a))
            ax.plot([x - dx, x + dx], [y - dy, y + dy], color="#3b8fd0", lw=0.7, zorder=5)
            for sgn in (1, -1):
                bx, by = x + sgn * 0.6 * dx, y + sgn * 0.6 * dy
                for b in (35, -35):
                    ang = np.radians(a + (0 if sgn > 0 else 180) + b + 180)
                    ax.plot([bx, bx + 0.45 * np.cos(ang)], [by, by + 0.45 * np.sin(ang)], color="#3b8fd0", lw=0.5,
                            zorder=5)

    def image(img, x, y, w, h, cmap=None, nearest=False):
        if img is None:
            ax.add_patch(plt.Rectangle((x, y), w, h, fc="#d9d9d9", ec="#777777", lw=0.4))
            return
        ax.imshow(img, extent=(x, x + w, y, y + h), cmap=cmap, interpolation="nearest" if nearest else "bilinear",
                  aspect="auto", zorder=2)
        ax.add_patch(plt.Rectangle((x, y), w, h, fc="none", ec="#555555", lw=0.4, zorder=3))

    def encoder(x, y, w, h):                  # trapezoid, narrowing to the right (down-sampling)
        ax.add_patch(Polygon([(x, y), (x, y + h), (x + w, y + h * 0.78), (x + w, y + h * 0.22)], closed=True,
                             fc="#d6e6f3", ec="#4f7ea6", lw=0.7))

    def head(x0, yc, step=4.2, wbar=2.6):
        for i, h in enumerate([13, 9.5, 9.5, 9.5, 9.5, 5.5]):
            xx = x0 + i * step
            ax.add_patch(FancyBboxPatch((xx, yc - h / 2), wbar, h, boxstyle="round,pad=0,rounding_size=1.0",
                                        fc="#d8c3e0" if i in (0, 5) else "#ece0f1", ec="#8a6a98", lw=0.6))
            if i:
                arr(xx - step + wbar + 0.1, yc, xx - 0.1, yc, lw=0.45)
        for i in range(1, 5):
            xx = x0 + i * step + wbar / 2
            ax.add_patch(FancyArrowPatch((xx - 2.2, yc + 5.6), (xx + 2.0, yc + 5.6), connectionstyle="arc3,rad=-0.9",
                                         arrowstyle="-|>", mutation_scale=4, color="#8a6a98", lw=0.45))
        return x0 + 5 * step + wbar

    rgb, dep, coord = thumbs if thumbs else (None, None, None)

    # ================================================================ Stage I: training on the room scans
    rbox(1, 54, 183, 69.5, STAGE1, lw=0.8, r=2.0)
    txt(3, 121.2, "Stage I: Room-scan training (once per room, before the exam)", fs=7.0, ha="left", va="top",
        weight="bold")
    txt(14, 116.2, "Room-scan frame $k$", fs=5.2)
    image(rgb, 5, 103.5, 18, 10.1)
    txt(14, 101.6, r"$\mathbf{I}_k \in \mathbb{R}^{3\times360\times640}$", fs=4.6)
    image(dep, 5, 86.5, 18, 10.1, cmap="viridis")
    txt(14, 84.6, r"$\mathbf{D}_k$: depth (mm)", fs=4.6)
    rbox(4.5, 61, 19, 18, ("#ffffff", "#2f6db5"))
    txt(14, 70, r"$\mathbf{T}_k \in SE(3)$" "\ncamera pose from\nself-mapping\n(scr_map.py; Polaris\nin benchmarks)", fs=4.3)

    # the network
    rbox(29, 87, 108, 29.5, ("#ffffff", "#9a9a9a"))
    txt(83, 114.6, r"SCR network $f_\theta$: image $\rightarrow$ room coordinate of every cell  (3.0 M parameters)",
        fs=5.2, weight="bold")
    rbox(31, 95, 12.5, 15, ("#f4f4f2", "#9a9a9a"))
    txt(37.25, 102.5, "Photometric\naug. $\\mathcal{A}$\nbrightness ±0.2\ncontrast ×0.8–1.2\ncolour ×0.9–1.1", fs=4.0)
    arr(23.4, 108.5, 30.8, 105.5)
    encoder(46.5, 91.5, 13, 21)
    txt(53.0, 102.5, "Encoder\nEfficientNet-B0\nblocks 0–5\nImageNet init.", fs=4.1)
    flame(57.8, 110.6)
    arr(43.7, 102.5, 46.3, 102.5)
    cells(63.5, 106.2, 4, CELL_A)
    txt(68.0, 110.4, r"$\mathbf{F}_8$: 40×45×80", fs=4.3)
    cells(63.5, 96.6, 4, CELL_B)
    txt(68.0, 93.6, r"$\mathbf{F}_{16}$: 112×23×40, bilinear ↑", fs=4.1)
    arr(59.7, 107.0, 63.3, 107.0)
    arr(59.7, 97.4, 63.3, 97.4)
    ax.add_patch(plt.Circle((80.5, 102.2), 1.9, fc="white", ec="#2b2b2b", lw=0.6))
    txt(80.5, 102.25, "C", fs=5.2, weight="bold")
    arr(72.8, 107.0, 79.0, 103.6)
    arr(72.8, 97.4, 79.0, 100.8)
    txt(80.5, 98.4, "concat\n152×45×80", fs=3.9, color=MUTED, va="top")
    hx = head(86.5, 102.2)
    arr(82.6, 102.2, 86.3, 102.2)
    flame(108.0, 110.6)
    txt(97.5, 92.2, "Coordinate head: 1×1 convs\n152→512, 4 residual blocks, 512→3", fs=4.1, color=MUTED)
    cells(118.5, 108.0, 5, "#b6b0d8", s=1.6, gap=0.5, vertical=True)
    arr(hx + 0.4, 102.2, 118.2, 102.2)
    txt(126.5, 106.0, r"$\hat{\mathbf{Y}}_k$", fs=5.6)
    txt(126.5, 101.0, "3×45×80\nprediction", fs=4.1, color=MUTED)

    # label generation
    rbox(29, 58, 108, 26, ("#ffffff", "#9a9a9a"))
    txt(31.5, 81.6, "Label generation (geometry, no learning)", fs=5.2, ha="left", va="top", weight="bold")
    txt(31.5, 75.6, r"$\mathbf{Y}_k(\mathbf{u}) = \mathbf{T}_k\,\pi^{-1}\!\left(\mathbf{u},\,\mathbf{D}_k(\mathbf{u})\right)$"
        "   room coordinate of cell $\\mathbf{u}$", fs=4.7, ha="left")
    txt(31.5, 70.4, r"$\mathbf{u}$: centre of each of the 45×80 cells (16×16 px of the 720×1280 image);"
        r"  $\pi^{-1}$: back-projection", fs=4.3, ha="left")
    txt(31.5, 65.2, r"$\mathbf{M}_k(\mathbf{u}) = 1$ only if $0.1 < \mathbf{D}_k(\mathbf{u}) < 2$ m"
        "  and the depth is not on an edge", fs=4.3, ha="left")
    txt(31.5, 60.6, "(far depth is noisy; an edge mixes two surfaces)", fs=4.0, ha="left", color=MUTED)
    image(coord, 115.5, 66.5, 18, 10.1, nearest=True)
    txt(124.5, 63.6, r"$\mathbf{Y}_k,\ \mathbf{M}_k$", fs=4.7)
    arr(23.4, 89.5, 28.8, 77.0)
    arr(23.9, 70.0, 28.8, 70.0)

    # objective
    rbox(141, 58, 41.5, 58.5, LOSS, lw=0.8, dashed=True)
    txt(161.75, 114.2, "Training objective", fs=5.6, weight="bold")
    txt(161.75, 110.0, r"$\mathcal{L}_{\mathrm{coord}} =$", fs=5.8)
    txt(161.75, 104.0, r"$\frac{1}{|\mathcal{M}|}\sum_{(k,\mathbf{u})\in\mathcal{M}}"
        r"\Vert\hat{\mathbf{Y}}_k(\mathbf{u})-\mathbf{Y}_k(\mathbf{u})\Vert_2$", fs=5.6)
    txt(161.75, 97.4, r"$\mathcal{M}$: labelled cells ($\mathbf{M}_k=1$) of all" "\nframes in the batch\n"
        "mean 3D (Euclidean) distance in m,\nnot squared: the only loss term", fs=4.3, color=MUTED, va="top")
    ax.plot([144, 179.5], [86.3, 86.3], color="#e2b5b2", lw=0.5)
    txt(161.75, 84.6, "AdamW, weight decay $10^{-4}$\nbatch 8, every room-scan frame\n120 epochs; lr warm-up,\n"
        "flat to 60 %, cosine to 0\nencoder $10^{-4}$, head $10^{-3}$\n~25–50 min on one GPU", fs=4.3, va="top")
    arr(129.6, 103.0, 140.8, 103.0)
    arr(133.8, 71.5, 140.8, 92.0)
    arr(161.75, 116.7, 100.0, 116.7, color="#c0504d", dashed=True, rad=0.07)
    txt(131.0, 120.6, r"back-propagate $\nabla_\theta\mathcal{L}_{\mathrm{coord}}$", fs=4.3, color="#c0504d")

    # ================================================================ Stage II: tracking during the exam
    rbox(1, 2, 183, 49.5, STAGE2, lw=0.8, r=2.0)
    txt(3, 49.4, "Stage II: Tracking during the exam (every frame; network frozen; no keypoints, no odometry)",
        fs=7.0, ha="left", va="top", weight="bold")
    txt(14, 44.6, "Sweep frame $t$", fs=5.2)
    image(rgb, 5, 31.8, 18, 10.1)
    txt(14, 29.9, r"$\mathbf{I}_t$", fs=4.8)
    image(dep, 5, 14.3, 18, 10.1, cmap="viridis")
    txt(14, 12.4, r"$\mathbf{D}_t$", fs=4.8)

    rbox(29.5, 31.5, 23, 11.5, ("#ece9fb", "#5b47c7"))
    txt(41.0, 37.25, r"$f_\theta$ from Stage I" "\n(frozen)", fs=4.8)
    snow(50.2, 40.9, 1.0)
    arr(23.4, 37.0, 29.3, 37.0)
    rbox(29.5, 12.5, 23, 13, ("#fff2dc", "#b8770b"))
    txt(41.0, 19.0, "Back-projection\n" r"$\mathbf{C}_t(\mathbf{u}) = \pi^{-1}(\mathbf{u},\mathbf{D}_t(\mathbf{u}))$"
        "\ncamera frame, 0.1–2 m", fs=4.3)
    arr(23.4, 19.3, 29.3, 19.3)

    rbox(58, 12.5, 32, 30.5, ("#ffffff", "#9a9a9a"))
    rng = np.random.default_rng(3)
    for k in range(5):
        yy = 34.0 + k * 1.3
        bad = k in (1, 4)
        ax.plot([63.5, 84.5], [yy, yy + rng.uniform(-0.4, 0.4)], color="#c94c4c" if bad else "#6d8f60", lw=0.45,
                ls=":" if bad else "-")
        ax.add_patch(plt.Circle((63.5, yy), 0.45, fc="#9fb7d6", ec="none"))
        ax.add_patch(plt.Circle((84.5, yy), 0.45, fc="#b6b0d8", ec="none"))
    txt(61.8, 36.6, r"$\mathbf{C}_t$", fs=4.8, ha="right")
    txt(86.2, 36.6, r"$\hat{\mathbf{Y}}_t$", fs=4.8, ha="left")
    txt(74.0, 25.6, "Dense 3D–3D pairs\n" r"$\{(\mathbf{C}_t(\mathbf{u}),\,\hat{\mathbf{Y}}_t(\mathbf{u}))\}$"
        "\none per cell (≤ 3,600)\nfixed by the cell grid:\nno keypoints, no matching", fs=4.3, va="center")
    arr(52.7, 37.0, 57.8, 35.5)
    arr(52.7, 19.3, 57.8, 21.0)

    rbox(95, 12.5, 26, 30.5, ("#fff2dc", "#b8770b"))
    txt(108.0, 27.75, "Kabsch RANSAC\n256 hypotheses (3 pairs each)\ninlier: "
        r"$\Vert\mathbf{T}\,\mathbf{C}_t(\mathbf{u})-\hat{\mathbf{Y}}_t(\mathbf{u})\Vert<20$ mm"
        "\n3 refits on the inliers\n≥ 400 inliers, else no pose\n\n" r"$\rightarrow\ \hat{\mathbf{T}}_t \in SE(3)$",
        fs=4.2)
    arr(90.2, 27.75, 94.8, 27.75)
    rbox(126, 12.5, 26, 30.5, ("#fff2dc", "#b8770b"))
    txt(139.0, 27.75, "Temporal smoothing\nrobust local fit of the poses\n"
        r"$\hat{\mathbf{T}}_{t'}$, $|t'-t| \leq 1$ s (offline)" "\nor last 1 s, 0.25 s delay\n(real time)\n\n"
        r"$\rightarrow\ \bar{\mathbf{T}}_t$", fs=4.2)
    arr(121.2, 27.75, 125.8, 27.75)
    rbox(157, 12.5, 25, 30.5, ("#ffffff", "#1f1f1e"))
    txt(169.5, 27.75, "US image pose\n" r"$\mathbf{T}^{\mathrm{US}}_t = \bar{\mathbf{T}}_t\,\mathbf{T}_{\mathrm{cam,US}}$"
        "\n(camera-to-US calib.,\nonce per probe)\n\n→ US images placed\nin the room:\n3D volume", fs=4.3)
    arr(152.2, 27.75, 156.8, 27.75)

    # legend
    flame(31.5, 5.6, 0.6)
    txt(33.3, 6.3, "trainable", fs=4.4, ha="left", color=MUTED)
    snow(47.5, 6.3, 0.9)
    txt(49.3, 6.3, "frozen", fs=4.4, ha="left", color=MUTED)
    ax.plot([59.5, 63.5], [6.3, 6.3], color="#c0504d", lw=0.7, ls="--")
    txt(64.5, 6.3, "training only", fs=4.4, ha="left", color=MUTED)
    rbox(79.5, 5.3, 3.2, 2.0, ("#fff2dc", "#b8770b"), lw=0.5, r=0.4)
    txt(83.5, 6.3, "geometry, no learning", fs=4.4, ha="left", color=MUTED)
    plt.rcParams["font.family"] = "DejaVu Sans"
    plt.rcParams["mathtext.fontset"] = "dejavusans"
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
    for name, make in (("scr_pipeline", pipeline), ("scr_architecture", lambda: architecture(thumbs)), ("scr_mapping", mapping)):
        fig = make()
        for ext in ("png", "pdf"):
            fig.savefig(Path(args.out_dir) / f"{name}.{ext}", dpi=400 if name == "scr_architecture" else 170, facecolor="white")
        plt.close(fig)
        print(f"wrote {Path(args.out_dir) / name}.png and .pdf")


if __name__ == "__main__":
    main()
