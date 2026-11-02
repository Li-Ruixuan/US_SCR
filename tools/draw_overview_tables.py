"""
The overview tables of summary.md 1.2 as figures, in tools/tables/: one PNG per table and all of
them in one PDF (one page each), with the conclusions of each table under it.
  A  every system at the US image          B  pose from one image (anchors)
  C  coverage: what decides SCR vs classical  D  where the error sits (absolute, shape, placement)
  E  every test and its verdict             F  map without a tracker (labels from the network's own map)

  python tools/draw_overview_tables.py              # -> tools/tables/table_<A..F>.png, tools/tables/overview_tables.pdf

The numbers are copied from summary.md (no run files are read): edit both together.
A cell starting with "*" is drawn bold (best in its column).
"""
import argparse
import textwrap
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

INK, MUTED, RULE, LIGHT = "#1f1f1e", "#6b6a63", "#1f1f1e", "#dddcd5"
HEAD = "#f2f1ec"
OURS = "#ece9fb"                     # the single-network system (purple, as in scr_pipeline)
CLASSICAL = "#fff4e2"                # the classical system (orange)
VERDICT = {"adopted": "#178a5e", "kept": "#178a5e", "SCR": "#178a5e", "odometry dropped": "#178a5e",
           "confirmed": "#178a5e", "real time works": "#178a5e", "no": "#b03a2e"}

TABLES = [
    dict(name="table_A", title="A. Every system: median error at the US image (mm), mean over sweeps",
         cols=["system", "2XX val", "3XX", "3XX strict", "4XX A", "4XX B", "4XX C", "4XX D", "4XX E",
               "4XX mean", "step 3XX / 4XX"],
         widths=[3.4, 0.62, 0.55, 0.72, 0.6, 0.6, 0.6, 0.6, 0.6, 0.75, 1.05],
         rows=[["classical odometry only (SIFT VO, each segment starts at the true pose)",
                "37.0", "9.4", "9.8", "15.1", "11.3", "8.9", "12.7", "12.9", "12.2", "–"],
               ["SCR every 0.25 s + RPRNet (learned) odometry, pose graph",
                "–", "3.2", "–", "5.4", "–", "–", "9.9", "–", "–", "1.51 / –"],
               ["SCR anchors (1 s) + SIFT odometry, pose graph (hybrid)",
                "4.2", "2.6", "–", "5.0", "5.7", "5.9", "9.6", "6.5", "6.54", "1.08 / 1.29"],
               ["classical anchors + SIFT odometry (classical system)",
                "4.2", "3.1", "3.0", "*4.2", "*3.4", "4.9", "*6.3", "*5.0", "*4.76", "1.09 / 1.28"],
               ["classical system, map = all same-day room scans up to the block",
                "–", "–", "–", "–", "5.5", "21.1", "18.9", "10.2", "–", "–"],
               ["one SCR network, raw", "3.59", "2.03", "3.12", "5.21", "5.82", "5.76", "9.57", "6.12", "6.50",
                "1.67 / 1.82"],
               ["one SCR network, 2 s smoothing (ours)",
                "3.35", "*1.85", "2.98", "5.14", "5.77", "5.63", "9.63", "6.25", "6.48", "*0.93 / 1.15"],
               ["one SCR network, all same-day room scans up to the block (ours, final; A unchanged)",
                "–", "–", "–", "5.14", "3.76", "3.98", "8.46", "5.92", "5.45", "– / 1.07"],
               ["same, real time with 0.25 s delay (window 1 s)",
                "3.32", "1.86", "*2.95", "5.14", "3.75", "3.98", "8.40", "5.88", "5.43", "0.93 / 1.06"],
               ["same, causal: no delay (window 0.25 s)",
                "*3.26", "1.95", "3.05", "5.22", "3.67", "*3.94", "8.43", "6.08", "5.47", "1.18 / 1.28"]],
         shade={3: CLASSICAL, 4: CLASSICAL, 6: OURS, 7: OURS, 8: OURS, 9: OURS},
         notes=["Odometry alone drifts (9–15 mm): every working system needs an absolute pose per frame or per second.",
                "The single network equals the hybrid on every split: SIFT odometry adds nothing once SCR runs on "
                "every frame; learned odometry is worse.",
                "Against classical: better on 2XX and 3XX, equal under the strict protocol; on 4XX 1.4× worse with each "
                "block's own scans, 1.15× with all scans of the day (C better); always the smoothest "
                "(step = change of the error over 8 rows).",
                "The same pooled scans ruin classical (C 4.9 → 21.1 mm): moved objects in earlier scans give confident "
                "wrong SIFT matches.",
                "Real time: a 0.25 s delay gives the offline result; fully causal only raises the steps by ~20 %, to "
                "classical's level."]),
    dict(name="table_B", title="B. Pose from one image: camera position error (median mm), one frame per second",
         cols=["method", "2XX val", "3XX", "4XX mean", "rotation 3XX / 4XX", "frames solved"],
         widths=[3.6, 0.75, 0.65, 0.85, 1.4, 1.9],
         rows=[["RPR anchor network (pose regression)", "–", "15.3", "49.0", "–", "3XX 93 %, 4XX 37–92 %"],
               ["SCR, first recipe, PnP", "15.8", "–", "–", "–", "all"],
               ["SCR v1 (fixed training), PnP", "5.1", "2.5", "11.1", "–", "all"],
               ["SCR v1, Kabsch on the measured depth", "*3.4", "2.0", "6.4", "*0.19° / 0.56°", "all"],
               ["SCR v2 (big head, clean labels), Kabsch", "*3.4", "*1.8", "6.0", "*0.19° / 0.49°", "all"],
               ["classical (SIFT matched to the room scan)", "5.2", "2.6", "*5.3", "0.34° / *0.38°", "all but A → C"]],
         shade={4: OURS, 5: CLASSICAL},
         notes=["The two big steps: training long enough (15.8 → 5.1 mm) and the measured depth at test time "
                "(PnP → Kabsch, 4XX 11.1 → 6.4 mm); head and labels mostly lower p90 and rotation.",
                "SCR is 8× more accurate than pose regression on both 3XX and 4XX.",
                "SCR vs classical follows Table A; on 4XX rotation is SCR's weak spot (0.49° vs 0.38°)."]),
    dict(name="table_C", title="C. What decides SCR vs classical: room-scan coverage (anchors, mm; US image where measured)",
         cols=["map (training data) → test", "sweep viewpoints covered", "SCR anchors", "classical anchors",
               "SCR / classical", "SCR system", "classical system"],
         widths=[3.5, 1.35, 1.25, 1.4, 0.95, 0.95, 0.95],
         rows=[["3XX, both room scans", "93–96 %", "*1.8", "2.6", "0.7", "*1.85", "3.1"],
               ["2XX val, both room scans", "75 %", "*3.4", "5.2", "0.65", "*3.35", "4.2"],
               ["3XX strict: room-301 only (recorded before the sweeps)", "fewer", "3.1 (v1)", "*2.7", "1.15",
                "*2.98", "3.0"],
               ["4XX, own room scans (40–90 s)", "0–14 %", "6.0", "*5.3", "1.13", "6.48", "*4.76"],
               ["A run-405…408, map + run-401…404 (Polaris labels)", "added views", "*2.0 (from 5.6)",
                "3.7 (from 5.9)", "0.54", "*2.3 (hybrid)", "3.2"],
               ["D run-421, 423, 424, map + run-418…420 (Polaris labels)", "added views", "*3.3 (from 8.6)",
                "4.7 (from 7.4)", "0.70", "*4.5 (hybrid)", "5.8"],
               ["B–E: all room scans of the day up to the block (objects moved between blocks)", "more, partly outdated",
                "–", "16.5 (from 5.0)", "–", "B 3.76, C 3.98, D 8.46, E 5.92", "5.5, 21.1, 18.9, 10.2"],
               ["same, labelled with the system's own poses", "added, wrong labels", "A 5.0 (from 5.3), D 7.9 (from 9.0)",
                "–", "–", "–", "–"],
               ["2XX map → 3XX (a few objects moved)", "outdated", "*6.5", "10.4", "0.63", "–", "–"],
               ["A map → B (small rearrangement)", "outdated", "14.0", "*7.9", "1.8", "–", "–"],
               ["A map → C (large rearrangement)", "outdated", "*13.4", "80.1 (21 % accepted)", "–", "–", "–"]],
         notes=["The SCR / classical ratio follows coverage: about 0.65–0.7 when the room scan covers the sweep "
                "viewpoints, about 1.1 when it does not.",
                "Real, correctly labelled views fix it, and SCR gains more from them than classical "
                "(A 5.6 → 2.0 vs 5.9 → 3.7 mm).",
                "Room scans of the same day, with objects moved since, help SCR (B–E 5.77, 5.63, 9.63, 6.25 → 3.76, 3.98, "
                "8.46, 5.92; mean 6.82 → 5.53) and ruin classical (3.4, 4.9, 6.3, 5.0 → 5.5, 21.1, 18.9, 10.2; mean "
                "4.90 → 13.93): the network learns what stays put, SIFT matches whatever it finds.",
                "Added views with wrong labels (self-labels) or poor synthesis (point-splat renders, Table E) "
                "do not help: the training views must be correct."]),
    dict(name="table_D", title="D. Where the error sits: error at the US image (mm), single network vs classical",
         cols=["split", "system", "absolute", "shape (after a rigid fit of each sweep)", "absolute − shape (placement)",
               "out-of-plane over 8 / 30 rows", "3D-page pixel error"],
         widths=[0.85, 2.2, 0.85, 1.55, 1.45, 1.4, 1.05],
         rows=[["2XX val", "one SCR network (ours)", "*3.36", "*3.04", "0.32", "0.47 / 1.09", "*3.8"],
               ["2XX val", "classical system", "4.22", "3.98", "0.24", "0.75 / 1.42", "5.1"],
               ["2XX val", "classical odometry only", "36.98", "14.26", "22.72", "0.69 / 1.44", "29.4"],
               ["3XX", "one SCR network (ours)", "*1.85", "*1.57", "0.28", "0.37 / 0.62", "*2.0"],
               ["3XX", "classical system", "3.11", "2.47", "0.64", "0.29 / 0.62", "3.2"],
               ["3XX", "classical odometry only", "9.43", "6.23", "3.20", "0.28 / 0.54", "10.1"],
               ["3XX strict", "one SCR network (ours)", "2.95", "*2.26", "0.69", "0.42 / 0.69", "3.2"],
               ["3XX strict", "classical system", "*2.91", "2.59", "0.32", "0.34 / 0.72", "3.2"],
               ["3XX strict", "classical odometry only", "9.77", "6.14", "3.63", "0.33 / 0.62", "10.4"],
               ["4XX mean", "one SCR network (ours)", "6.49", "*3.17", "3.32", "0.39 / 0.74", "7.1"],
               ["4XX mean", "classical system", "*4.75", "3.34", "1.41", "0.39 / 0.76", "*5.2"],
               ["4XX mean", "classical odometry only", "12.19", "6.66", "5.53", "0.41 / 0.86", "12.5"],
               ["4XX pooled", "one SCR network, same-day scans (A–E)", "5.45", "*2.95", "2.50", "0.38 / 0.69", "6.0"],
               ["4XX pooled", "classical system, same-day scans (B–E)", "13.92", "8.30", "5.62", "0.46 / 1.12", "15.5"]],
         shade={0: OURS, 1: CLASSICAL, 3: OURS, 4: CLASSICAL, 6: OURS, 7: CLASSICAL, 9: OURS, 10: CLASSICAL,
                12: OURS, 13: CLASSICAL},
         group=0, left=2,
         notes=["Between nearby frames all three are the same (0.3–0.4 mm over 8 rows): local motion is solved by any.",
                "The single network's volume shape is better than classical's on every split mean: 2XX 3.04 vs 3.98, "
                "3XX 1.57 vs 2.47, 3XX strict 2.26 vs 2.59, 4XX 3.17 vs 3.34 "
                "(A 2.92 vs 3.10, B 2.66 vs 2.47, C 2.96 vs 3.36, D 3.16 vs 3.61, E 4.16 vs 4.15).",
                "The whole 4XX gap is placement: each sweep is shifted rigidly in the room (3.3 vs 1.4 mm), an anchoring "
                "error, consistent with the coverage finding of Table C.",
                "With all same-day scans, the single network's shape is better than classical's (own scans) on every 4XX "
                "split: A 2.92 vs 3.10, B 2.19 vs 2.47, C 2.55 vs 3.36, D 3.36 vs 3.61, E 3.75 vs 4.15."]),
    dict(name="table_E", title="E. Every test and its verdict (anchors = camera position median, US = system at the US image, mm)",
         cols=["area", "test", "measured on", "result", "verdict"],
         widths=[0.75, 3.5, 1.75, 2.9, 1.5],
         rows=[["training", "fixed recipe, 15 → 120 epochs", "2XX anchors (PnP)", "15.8 → 5.1", "adopted"],
               ["training", "full resolution 720 × 1280 (30 epochs)", "2XX anchors", "6.3 → 7.3", "no"],
               ["training", "viewpoint augmentation (zoom, rotation)", "2XX anchors", "3.4 → 6.5", "no"],
               ["training", "big head + clean labels (v2)", "2XX p90, rotation", "8.7 → 7.3, 0.33° → 0.27°", "adopted"],
               ["training", "frozen ImageNet encoder", "4XX A US", "5.14 → 5.24", "no"],
               ["training", "+ rendered views (point splats)", "4XX A US", "5.14 → 4.98", "no (rule: ≥ 0.5 better)"],
               ["training", "frozen encoder + rendered views", "4XX A US", "5.14 → 5.51", "no"],
               ["training", "seeds 0 / 1 / 2", "3XX US", "1.85 / 1.95 / 2.12", "noise ≈ 0.3 mm"],
               ["training", "240 instead of 120 epochs", "4XX A US (fit)", "5.14 → 5.28 (fit 1.24 → 1.05)", "no"],
               ["training", "rendered views from real frames (full resolution)", "4XX A US", "5.14 → 4.94",
                "no (rule: ≥ 0.5 better)"],
               ["training", "confidence head (unweighted solver)", "4XX A US", "5.14 → 5.22", "neutral"],
               ["pose", "pose regression (RPR) instead of SCR", "3XX / 4XX anchors", "15.3 / 49.0 vs 1.8 / 6.0", "SCR"],
               ["pose", "Kabsch on measured depth instead of PnP", "2XX anchors", "5.1 → 3.4", "adopted"],
               ["pose", "refined pose fit (noise weights; reprojection + depth)", "2XX anchors", "3.4 → 4.7 / 3.6", "no"],
               ["pose", "inlier gate ≥ 400", "all splits", "trims tails on D, E, A → C", "kept"],
               ["pose", "multi-frame anchors (3 / 5 frames)", "2XX US (hybrid)", "4.2 → 4.4 / 4.5", "no"],
               ["pose", "confidence-weighted Kabsch (same checkpoint)", "4XX A US", "5.22 → 5.28", "no"],
               ["time", "SIFT odometry + pose graph vs one network", "4XX mean US", "6.54 vs 6.48", "odometry dropped"],
               ["time", "RPRNet (learned) odometry instead of SIFT", "3XX / A / D US", "0.3–0.6 worse", "no"],
               ["time", "2 s robust smoothing vs raw", "3XX US (step)", "2.03 (1.67) → 1.85 (0.93)", "adopted"],
               ["time", "real time: 0.25 s delay / causal", "3XX US (step)", "1.85 (0.93) → 1.86 (0.93) / 1.95 (1.18)",
                "real time works"],
               ["time", "pose graph with zero-motion odometry", "3XX US", "2.0 → 4.9", "no"],
               ["time", "gate recovery (hybrid only)", "run-404 US", "28.3 → 8.2", "kept"],
               ["time", "pose-graph anchor σ 11 / 5 / 3 mm", "2XX US", "4.4 / 4.4 / 4.5", "default kept"],
               ["map", "+ earlier sweeps, Polaris labels", "4XX A / D anchors", "5.6 → 2.0 / 8.6 → 3.3", "works, needs Polaris"],
               ["map", "+ same-day room scans (A, B scans for C, D, E)", "4XX C / D / E US",
                "5.63 / 9.63 / 6.25 → 3.98 / 8.46 / 5.92", "adopted"],
               ["map", "same for B (A + B scans), as confirmation", "4XX B US", "5.77 → 3.76", "confirmed"],
               ["map", "classical system with the same pooled map", "4XX B / C / D / E US",
                "3.4 / 4.9 / 6.3 / 5.0 → 5.5 / 21.1 / 18.9 / 10.2", "no"],
               ["map", "+ earlier sweeps, labelled with own poses", "4XX A / D anchors", "5.3 → 5.0 / 9.0 → 7.9", "no"],
               ["map", "strict protocol (room-301 only)", "3XX run-315…317 US", "1.85 → 2.98 (classical 3.0)", "report both"],
               ["map", "outdated map (previous session)", "anchors", "2XX → 3XX 6.5; A → B 14.0; A → C 13.4",
                "re-scan per session"],
               ["map", "shorter room scans: first 20 / 40 s of each", "3XX US", "3.00 / 2.03 vs 1.85 (~60 s)",
                "content over length"],
               ["map", "map without a tracker: the network + depth ICP build the room-scan poses (labels)", "3XX US / shape",
                "1.85 / 1.57 (Polaris labels) → 13.26 / 8.54", "works, not accurate"],
               ["map", "map aligned to Polaris on view points, not camera positions (evaluation)", "3XX US", "50.6 → 12.8",
                "fixed"],
               ["map", "joint refinement of network and map poses", "3XX map camera position", "8.4 → 8.9", "no"],
               ["map", "+ pose graph over the room scan (depth ICP edges + network priors)", "3XX US / shape",
                "13.26 / 8.54 → 12.49 / 4.74", "adopted"],
               ["map", "pose-graph prior 10 / 30 mm", "3XX map scene points", "6.9 / 7.3", "default kept"],
               ["US", "U1 in-plane registration (ECC)", "2XX, 10 rows", "1.91 vs 1.55 for zero motion", "no"],
               ["US", "U2 speckle decorrelation → distance", "all", "0.27–0.43, magnitude only", "no"],
               ["US", "U3 per-patch speckle vs camera", "3XX, 4 rows", "0.78 vs camera 0.19", "no"],
               ["US", "Li et al. reproduced on its own data", "their test set", "21.4 vs 22.8 published", "reproduced"],
               ["US", "Li et al. on our sweeps", "3XX / A / D", "zero-shot 129; fine-tuned 75–125; scratch = zero motion",
                "no"]],
         group=0, verdict=4, left=4,
         notes=["Adopted: longer training, Kabsch on depth, big head + clean labels, 2 s smoothing, pooled same-day "
                "room scans; real time with a 0.25 s delay; for maps without a tracker, the pose graph. Everything else is "
                "neutral or worse; odometry and every US-image method were dropped."]),
    dict(name="table_F", title="F. Map without a tracker (3XX): training labels from a map the network builds itself "
                               "(Polaris for evaluation only; mm)",
         cols=["training labels from", "map: scene points at 1 m", "map: camera position", "map: 1 s motion",
               "US: absolute", "US: shape (after a rigid fit of each sweep)", "placement (absolute − shape)",
               "out-of-plane over 8 / 30 rows", "step over 8 rows"],
         widths=[2.7, 0.95, 0.95, 0.85, 0.85, 1.3, 1.15, 1.2, 0.8],
         rows=[["Polaris (reference)", "–", "–", "–", "*1.85", "*1.57", "0.28", "0.37 / 0.62", "*0.93"],
               ["map, each frame localised on its own", "9.0", "15.3", "7.2", "13.26", "8.54", "4.72", "0.46 / 1.14", "1.39"],
               ["map + pose graph (depth ICP edges, network priors 10 mm)", "*6.9", "*11.6", "*3.4", "12.49", "4.74",
                "7.75", "0.46 / 1.24", "1.14"],
               ["map + pose graph, priors 30 mm (map only, not trained)", "7.3", "12.2", "3.4", "–", "–", "–", "–", "–"],
               ["classical system (needs no labels)", "–", "–", "–", "3.11", "2.47", "0.64", "0.29 / 0.62", "–"],
               ["classical odometry only", "–", "–", "–", "9.43", "6.23", "3.20", "0.28 / 0.54", "–"]],
         shade={0: OURS, 2: OURS, 4: CLASSICAL}, left=1,
         notes=["The network reproduces its labels: the same network gives 1.85 mm with Polaris labels and 12.5–13.3 mm "
                "with map labels. More training cannot help; the map decides.",
                "The pose graph ties neighbouring room-scan frames together: the map's 1 s motion error halves (7.2 → 3.4) "
                "and the volume shape improves from 8.54 to 4.74 (per sweep 1.9–4.4, run-317 9.8): better than odometry "
                "alone (6.23), still 2–3× Polaris labels (1.57) and classical (2.47).",
                "What is left of the absolute error is one fixed offset in the camera frame, the same in every sweep "
                "(9.6 mm, 0.4°; spread 1–2 mm over sweeps): the signature of a hand–eye mismatch between Polaris and the "
                "camera, not of the map. Removing it (estimated on the other sweeps) brings the difference to the "
                "Polaris-labelled track from 8.4–12.2 to 2.2–4.3 mm (run-317 7.9; proxy, not yet against Polaris).",
                "A looser prior (30 mm) gives the same 1 s motion (3.4): the remaining local error sits in the ICP edges "
                "(or the hand–eye of the evaluation), not in the priors."]),
]


def draw(t, fs=8.5):
    widths, cols, rows = t["widths"], t["cols"], t["rows"]
    shade, group, verdict, left = t.get("shade", {}), t.get("group"), t.get("verdict"), t.get("left", 1)
    lh, pad, x0 = fs / 72 * 1.3, 0.07, 0.2
    char = fs / 72 * 0.55

    def wrap(s, w):
        return textwrap.wrap(s, max(4, int((w - 2 * pad) / char))) or [""]

    W = sum(widths) + 2 * x0
    head = [wrap(c, w) for c, w in zip(cols, widths)]
    body = [[wrap(c.lstrip("*"), w) for c, w in zip(r, widths)] for r in rows]
    notes = [wrap("•  " + n, W - 2 * x0) for n in t.get("notes", [])]
    hh = max(map(len, head)) * lh + 2 * pad
    rh = [max(map(len, r)) * lh + 2 * pad for r in body]
    top = 0.5
    H = top + hh + sum(rh) + 0.2 + sum(len(n) for n in notes) * lh + 0.1 * len(notes) + 0.15
    fig = plt.figure(figsize=(W, H), facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(H, 0)
    ax.axis("off")
    xs = [x0 + sum(widths[:i]) for i in range(len(widths) + 1)]

    def cell(i, y, lines, bold=False, color=INK):
        ha = "left" if i < left else "center"
        x = xs[i] + pad if i < left else (xs[i] + xs[i + 1]) / 2
        ax.text(x, y + pad, "\n".join(lines), ha=ha, va="top", fontsize=fs, color=color, linespacing=1.3,
                fontweight="bold" if bold else "normal")

    ax.text(x0, 0.18, t["title"], fontsize=fs + 2.5, fontweight="bold", color=INK, va="top")
    y = top
    ax.add_patch(Rectangle((xs[0], y), xs[-1] - xs[0], hh, color=HEAD, lw=0))
    ax.plot([xs[0], xs[-1]], [y, y], color=RULE, lw=1.2)
    for i, lines in enumerate(head):
        cell(i, y, lines, bold=True)
    y += hh
    ax.plot([xs[0], xs[-1]], [y, y], color=RULE, lw=0.8)
    prev = None
    for r, (raw, lines, h) in enumerate(zip(rows, body, rh)):
        if r in shade:
            ax.add_patch(Rectangle((xs[0], y), xs[-1] - xs[0], h, color=shade[r], lw=0))
        new_group = group is not None and raw[group] != prev
        if r and new_group:
            ax.plot([xs[0], xs[-1]], [y, y], color=MUTED, lw=0.7)
        elif r:
            ax.plot([xs[0], xs[-1]], [y, y], color=LIGHT, lw=0.5)
        for i, (s, ls) in enumerate(zip(raw, lines)):
            if i == group and not new_group:
                continue
            color = INK
            if i == verdict:
                color = VERDICT.get(s, VERDICT["no"] if s.startswith("no ") else INK)
            cell(i, y, ls, bold=s.startswith("*") or i == group or (i == verdict and color != INK), color=color)
        prev = raw[group] if group is not None else None
        y += h
    ax.plot([xs[0], xs[-1]], [y, y], color=RULE, lw=1.2)
    y += 0.2
    for n in notes:
        ax.text(x0, y, "\n".join(n), fontsize=fs, color=INK, va="top", linespacing=1.3)
        y += len(n) * lh + 0.1
    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(Path(__file__).resolve().parent / "tables"))
    args = ap.parse_args()
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with PdfPages(out / "overview_tables.pdf") as pdf:
        for t in TABLES:
            fig = draw(t)
            fig.savefig(out / f"{t['name']}.png", dpi=200, facecolor="white")
            pdf.savefig(fig, facecolor="white")
            plt.close(fig)
            print(f"{t['name']} -> {out / t['name']}.png")
    print(f"all -> {out / 'overview_tables.pdf'}")


if __name__ == "__main__":
    main()
