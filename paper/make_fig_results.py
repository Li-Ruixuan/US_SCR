"""
Paper figures drawn from the committed result files only (no recordings needed):

  fig_orbslam_persweep   every evaluated sweep: our error against ORB-SLAM3 relocalising each frame against its
                         frozen room-scan map (both at the US image, smoothed 1 s), by session
  fig_occlusion          controlled occlusion (S-ctrl B, C): per-sweep error of ours and of ORB-SLAM3 in three
                         modes, without the occluder and with 30 / 60 % of the image width occluded

  python paper/make_fig_results.py            # writes paper/figures/<name>.pdf and .png

Sources: runs/<track folder>/scr_track.json (ours, "smoothed 1 s") and runs/slam-*/slam_eval.json (ORB-SLAM3).
Session names as in the paper: S-test = 3XX, S-new = 4XX, S-ctrl = 5XX.
"""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
RUNS, OUT = REPO / "runs", REPO / "paper" / "figures"

# categorical slots 1-4 of the dataviz reference palette (validated in this order), plus marker shapes
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
INK, MUTED, RULE = "#1f1f1e", "#5f5e58", "#d9d8d0"

plt.rcParams.update({"font.family": "sans-serif", "font.size": 8, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.linewidth": 0.6, "pdf.fonttype": 42})


def ours(folder):
    d = json.load(open(RUNS / folder / "scr_track.json"))["per_sweep"]["smoothed 1 s"]
    return {k: v["us_median"] for k, v in d.items()}


def orb(folder):
    d = json.load(open(RUNS / folder / "slam_eval.json"))["sweeps"]
    return {k: v["us_median"] for k, v in d.items()}


def clean(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(True, which="major", color=RULE, linewidth=0.5)
    ax.set_axisbelow(True)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=600 if ext == "png" else None, bbox_inches="tight")
    print(f"-> {OUT / name}.pdf / .png")


def fig_persweep():
    groups = [  # label, colour, marker, [(our track folder, ORB-SLAM3 folder)]
        ("S-test", BLUE, "o", [("repro/track-v2map-3XX", "slam-3XX-reloc")]),
        ("S-new", ORANGE, "s", [(f"track-v2map-4XX{b}", f"slam-4XX{b}-reloc") for b in "ABCDE"]),
        ("S-ctrl, exam-view scans", AQUA, "^", [(f"track-v2map-5XX{b}-exam", f"slam-5XX{b}-exam-reloc") for b in "ABCDE"]),
        ("S-ctrl A, generic scan", YELLOW, "D", [("track-v2map-5XXA-generic", "slam-5XXA-generic-reloc")]),
    ]
    fig, ax = plt.subplots(figsize=(3.4, 3.5))
    lim = (0.8, 25)
    ax.plot(lim, lim, color=MUTED, linewidth=0.8, zorder=1)
    n_all = n_ours = 0
    for label, col, mk, pairs in groups:
        x, y = [], []
        for a, b in pairs:
            oa, ob = ours(a), orb(b)
            for k in oa:
                if k in ob and np.isfinite(oa[k]) and np.isfinite(ob[k]):
                    x.append(oa[k]), y.append(ob[k])
        x, y = np.array(x), np.array(y)
        if label != "S-ctrl A, generic scan":
            n_all += len(x)
            n_ours += int((x < y).sum())
        ax.scatter(x, y, s=16, color=col, marker=mk, edgecolors="white", linewidths=0.5, label=f"{label} ({len(x)})",
                   zorder=3)
    ax.set_xscale("log"), ax.set_yscale("log")
    ax.set_xlim(lim), ax.set_ylim(lim)
    ticks = [1, 2, 5, 10, 20]
    ax.set_xticks(ticks), ax.set_yticks(ticks)
    ax.set_xticklabels(ticks), ax.set_yticklabels(ticks)
    ax.minorticks_off()
    ax.set_xlabel("Ours, error at the US image (mm)")
    ax.set_ylabel("ORB-SLAM3, each frame relocalised (mm)")
    ax.text(1.0, 18, "ours lower", color=MUTED, fontsize=7)
    ax.text(9, 1.0, "ORB-SLAM3 lower", color=MUTED, fontsize=7)
    clean(ax)
    ax.legend(frameon=False, fontsize=7, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=2, handletextpad=0.2,
              columnspacing=0.8)
    fig.tight_layout()
    save(fig, "fig_orbslam_persweep")
    print(f"   ours lower on {n_ours} of {n_all} sweeps with current maps")


def fig_occlusion():
    systems = [  # label, colour, marker, folder pattern for (block, tag)
        ("Ours", BLUE, "o", lambda b, t: ("ours", f"track-v2map-5XX{b}-exam{t}")),
        ("ORB-SLAM3, full SLAM", ORANGE, "s", lambda b, t: ("orb", f"slam-5XX{b}-exam{t}-online")),
        ("ORB-SLAM3, localisation only", AQUA, "^", lambda b, t: ("orb", f"slam-5XX{b}-exam{t}-loc")),
        ("ORB-SLAM3, each frame relocalised", YELLOW, "D", lambda b, t: ("orb", f"slam-5XX{b}-exam{t}-reloc")),
    ]
    levels = [("none", ""), ("30 %", "-occ30"), ("60 %", "-occ60")]
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 2.7))
    rng = np.random.default_rng(0)
    for ax, (b, name) in zip(axes, [("B", "S-ctrl B"), ("C", "S-ctrl C")]):
        for li, (lname, tag) in enumerate(levels):
            for si, (slabel, col, mk, folder) in enumerate(systems):
                kind, f = folder(b, tag)
                vals = ours(f) if kind == "ours" else orb(f)
                v = np.array([x for x in vals.values() if np.isfinite(x)])
                xc = li + (si - 1.5) * 0.19
                ax.scatter(xc + rng.uniform(-0.04, 0.04, len(v)), v, s=12, color=col, marker=mk, edgecolors="white",
                           linewidths=0.4, zorder=3, label=slabel if li == 0 else None)
                missing = len(vals) - len(v)
                if missing:
                    ax.text(xc, 120, f"{missing} of {len(vals)}\nnot posed", ha="center", va="bottom", fontsize=6,
                            color=MUTED)
        ax.set_yscale("log")
        ax.set_ylim(0.8, 250)
        ax.set_yticks([1, 2, 5, 10, 20, 50, 100])
        ax.set_yticklabels([1, 2, 5, 10, 20, 50, 100])
        ax.minorticks_off()
        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels([f"occluded: {n}" for n, _ in levels])
        ax.set_xlim(-0.5, len(levels) - 0.5)
        ax.set_title(name, fontsize=8, color=INK, loc="left")
        clean(ax)
    axes[0].set_ylabel("Error at the US image per sweep (mm)")
    h, lab = axes[0].get_legend_handles_labels()
    fig.tight_layout(rect=(0, 0.1, 1, 1))
    fig.legend(h, lab, frameon=False, fontsize=7, loc="lower center", ncol=4, bbox_to_anchor=(0.5, 0.0),
               handletextpad=0.2, columnspacing=1.2)
    save(fig, "fig_occlusion")


if __name__ == "__main__":
    fig_persweep()
    fig_occlusion()
