# Writing brief: TBME paper on tracker-free freehand 3D US

Start a new chat with: "Read `tools/paper/writing_brief.md`, then `paper/generic-color-brief.tex`. This chat is only about writing the paper."

Last updated 17 Nov 2026.

## 1. Rules for this chat

- **Scope.** Write and edit the paper. Do not change the code, run experiments or regenerate data.
- **No git.** Never commit or push. When files change, give the user the git commands, and never stage `note.md`.
- **No runs on this machine.** All training, processing and data-heavy figure scripts run on the training PC; give plain foreground `python ...` commands.
- **Facts come from the repo.** Every number must come from the draft, the code (`scr_anchor.py`, `scr_map.py`, `scr.py`, `baselines/`, `tools/`) or the result files in `runs/`. Never invent or round a number to make a sentence work. If a value is missing, keep or add a red placeholder (`\NUMQ{...}`, `\tbd{...}`).
- **Edits.** You may edit `paper/generic-color-brief.tex` directly. Make small edits, say what changed, and keep every claim honest.
- **Paper folder.** `paper/` is the Overleaf folder: only the .tex, cls/sty, bib, logo and the final figures, all flat at the .tex level. Use one format per figure (PNG, except `fig_overview.pdf`) and no unused files. Figure sources, scripts and notes go in `tools/paper/`.

## 2. Framing (decided by the user, do not re-argue)

- **Not a better ORB-SLAM3.** The paper presents a *different, data-driven solution*. ORB-SLAM3 is the honest reference and is more accurate like for like (also with its map frozen and every frame relocalised). Never write that we "beat", "outperform" or "rival" it.
- **What we offer instead:**
  - per-frame localisation with no tracking state;
  - a bounded error under occlusion;
  - detectable failures (coverage check, median-inlier check);
  - no external hardware during the exam;
  - explicit operating conditions, turned into a room-scan protocol.
- **The main finding is coverage.** The room scan must cover the examination views. This is a limit of scene coordinate regression, not of self-mapping: the oracle map fails too, and ORB-SLAM3 does not.
- **Placement versus shape.** The tracker-free error is mostly a placement of the whole sweep. The shape of the volume is preserved.

## 3. Files

| File | What it is |
|---|---|
| `paper/generic-color-brief.tex` | The draft (IEEE TBME, `ieeecolor2`, `9pt,shortpaper,twoside,web`) |
| `paper/bib.bib` | References; `TODO-*` entries are placeholders |
| `paper/2026_UCL_tracker_free_US_RGB_D_TBME.pdf` | User's last Overleaf compile (may be older than the .tex) |
| `paper/fig_overview.pdf` | Fig. 1: (a) before the exam, (b) per frame, (c) network, labels and loss |
| `paper/fig_volume_coverage.png` | S-ctrl A sweep: exam-view map vs generic map, as placed and after the rigid fit |
| `paper/fig_coverage_error.png` | Error vs coverage; error vs map camera error |
| `paper/fig_volume_snew.png` | S-test and S-new volumes, as placed and after the rigid fit |
| `paper/fig_volume_outdated.png` | S-ctrl C with its own map vs B's outdated map, plus inlier counts |
| `paper/fig_orbslam_persweep.png` | Per-sweep scatter, ours vs ORB-SLAM3 (each frame relocalised) |
| `paper/fig_occlusion.png` | Per-sweep error under synthetic occlusion |
| `tools/paper/fig_overview.tex` + `thumbs/` | TikZ source of Fig. 1. Build: `tectonic tools/paper/fig_overview.tex`, then `cp tools/paper/fig_overview.pdf paper/` |

The scripts that made the PNG figures (`make_fig_results.py`, `make_fig_volumes.py`, `make_thumbnails.py`) are only in git history: `git show 8d570109:paper/<name>`. They need the training PC.

**Compiling locally.**
- Overleaf (pdfLaTeX, Times) is the reference for layout and page count.
- A local XeTeX/tectonic build uses wider fonts and overestimates the length. It also needs the EPS logo converted to PDF.
- Last local count: 11 pages, last page about 60 % full, which is about 10 pages in Overleaf.

## 4. Names and conventions

- **Sessions.** Use `\Sval`, `\Stest`, `\Snew`, `\Sctrl` (S-val, S-test, S-new, S-ctrl). The repo uses 2XX, 3XX, 4XX and 5XX respectively.
  - Never put run numbers, session codes or folder names in the paper or its figures.
- **ORB-SLAM3 modes.** Use `\fullslam`, `\loconly`, `\reloc` (full SLAM, localisation only, each frame relocalised). Poses are scored *as tracked*; full SLAM is also scored *refined at shutdown*.
- **Maps.**
  - *Self-mapped*: ours.
  - *Oracle map*: the same network trained on tracker poses of the room scan.
  - *Exam-view* vs *generic* room scan.
  - *Outdated*: an earlier block's map.
  - *Strict protocol*: only the room scan recorded before the sweeps.
- **Errors.** Measured at the US image, 5 points; median per sweep, then the mean over sweeps.
  - *Absolute*: one rigid alignment per session.
  - *Shape*: best rigid fit per sweep.
  - Also: worst sweep, out-of-plane error over 8 / 30 rows, jitter, anchors, posed, coverage, map error.
- **Notation.** `T^A_B` maps B to A; lengths in mm.
  - Frames: W map, C camera, U image, M marker.
  - `X` is the probe calibration in the camera frame. `T^C_U` is the camera-to-image calibration. `S = diag(s,s,1,1)`, with s = 0.23 mm/px.
  - `n_t` is the inlier count; the gate is 400.
- **Style.**
  - British spelling (localisation, normalised).
  - Plain, factual sentences; numbers with units (`2.34\,mm`); ranges with `--`; `\,\%`.
  - Tables use booktabs and `\scriptsize`, written as "absolute / shape".
  - No marketing words ("novel", "robust", "state-of-the-art", "significantly" unless it is a test result).
  - Each claim says which session and which mode it refers to.

## 5. Key facts (method, from the code)

- **Network.**
  - Encoder: ImageNet EfficientNet-B0, blocks 0–3 (stride 8, 40 channels) plus blocks 4–5 (stride 16, 112 channels, upsampled), concatenated to 152 channels.
  - Head: 1×1 convs, 152→512, 4 residual blocks, 512→3; 3.0 M parameters.
  - Input 360×640 RGB, so the output is 45×80 cells of 16×16 px at full resolution.
  - Outputs metres relative to the scene centre (mean camera position of the training frames).
  - The head runs in FP32, the encoder in mixed precision.
  - `SCRNet` in `scr.py` (head 152→256) is the older library network; the final head is `BigHead` in `scr_anchor.py`.
- **Training.**
  - Loss: mean unsquared 3D distance.
  - Labels: depth 0.1–2 m, no depth edge (>6 % jump to a neighbour).
  - AdamW: lr 1e-3 for the head and 1e-4 for the encoder, weight decay 1e-4, batch 8, 120 epochs (40 give the same accuracy).
  - Schedule: 1 % warm-up, flat to 60 %, cosine to zero.
  - Augmentation: photometric only.
  - S-test: 3356 frames, 419 iterations per epoch.
- **Pose.**
  - Kabsch RANSAC: 256 samples of 3 cells, 20 mm inlier threshold, 3 refits. No prior pose is used.
  - Inlier gate: 400.
- **Self-mapping.**
  - Seeding: seed frame plus depth ICP over ±2 s (own point-to-plane ICP, ≤8000 points, 10 iterations, 40→10 mm).
  - Rounds: training 2000 steps, then 1500 per round. Frames join at ≥60 inliers with plausible motion, or every 30th frame at ≥400 inliers. ICP extends each placed segment by up to 90 frames.
  - Stop when a round adds fewer than 0.5 % of the frames.
  - Pose graph: sequential edges plus loop-closure ICP edges, point residuals, soft-L1, σ_e = 1 mm, σ_p = 10 mm, SciPy trf, ≤300 evaluations.
  - The final network is retrained from scratch on the optimised poses.
- **Probe calibration X.** Fitted once on S-test with A (alignment) and reused on S-new and S-ctrl. Uses a soft-L1 loss with a 5 mm scale.
- **Smoothing.** Tricube-weighted local polynomial with Tukey reweighting.
  - Offline: ±1 s.
  - Real time: 0.25 s delay.
  - Causal: last 0.25 s.
- **Compounding.** 0.4 mm voxels, nearest voxel, mean. The display is a 6 mm slab MIP.
- **Hardware and timing.**
  - Sensors: RealSense D435i (1280×720, ~30 Hz); NDI Polaris Vega; US 640×480 at 0.23 mm/px, 9 cm depth, 19 fps.
  - Computer: RTX A4500.
  - Self-mapping ~30 min; training 40 min (120 epochs) or 13 min (40 epochs); tracking 60–70 ms per frame. ORB-SLAM3 relocalisation: 25–41 ms on the CPU.
- **ORB-SLAM3.** Commit 4452a3c (10 Feb 2022), RGB-D, 1250 features. One-line change so that it relocalises in localisation mode.

## 6. Key results (as in the draft; the draft is authoritative)

- **S-test:**
  - Ours: 2.34 / 1.72 mm (3 seeds: 2.22–2.34). Oracle map: 1.85 / 1.57.
  - Classical pipeline: 3.11 / 2.47. Odometry only: 9.43 / 6.23.
  - ORB-SLAM3: 1.72–1.84 / 1.18–1.38.
  - Strict protocol: 2.94. Real time: 2.34. Causal: 2.42.
- **S-ctrl, exam-view scans (absolute):** A 2.28, B 4.43 (75 % coverage), C 3.11, D 2.24, E (emptied room) 5.85. Shape 1.70–1.90 mm on A, C and D.
- **Coverage (S-ctrl A):**
  - Generic scan (0 % coverage): ours 13.57, oracle map 10.95, ORB-SLAM3 2.76–2.88.
  - Both scans in one map: 3.15.
  - Frame level, oracle map: 4.1 mm within 30 mm and 10° of a room-scan pose, 13.4 mm otherwise.
- **Self-mapping ablations (S-test):** without loop closures 5.77 / 3.18; without X 11.49 / 4.08. Map error: 2.0 mm at the camera, 0.19°.
- **S-new (generic scans, 0–14 % coverage):** ours 7.92 / 2.69, oracle map 6.48 / 3.17, classical 4.76 / 3.34, ORB-SLAM3 (localisation only) 4.45 / 1.34 on blocks A–D.
- **Outdated maps:**
  - A's map on B: 4.28.
  - A's map on C: 59.4 (21 % posed). B's map on C: 40.9.
  - C's map on E: 13.9.
  - Median inliers: 1371–2213 with current maps, 23–450 when the map fails.
- **ORB-SLAM3 comparison:**
  - Each frame relocalised: lower on 52 of 63 sweeps, on average 1.96 mm lower [1.30, 2.61], Wilcoxon p < 0.001.
  - Ours is lower only on S-ctrl A with the exam-view scan.
- **Occlusion (S-ctrl B and C, 30 / 60 % of the image width):**
  - Ours: +0.4–0.9 mm, no sweep above 8.5 mm.
  - ORB-SLAM3: lower mean in 9 of 12 settings, but single sweeps fail by 13–132 mm while it reports tracking.
- **Pose regression:** about 8× worse anchors than SCR (S-test 1.8 vs 15.3 mm).

## 7. Open items

1. **Placeholders the user must fill** (red in the PDF):
   - Depth alignment method (Problem Statement, end of the paragraph after Eq. 1).
   - Set-Up and Ground Truth:
     - probe and scanner model;
     - hand–eye calibration (number of views, board, solver);
     - US calibration (phantom, method, reference, residual);
     - clock and timestamp matching;
     - phantom type; ethics approval;
     - code availability.
2. **References.**
   - 11 `TODO-*` placeholder entries in `bib.bib` (clinical 3D US, freehand review, point-of-care, EM distortion, elevational beam width, speckle decorrelation, Low 2004 ICP, PoseNet, endoscopic relocalisation, classical pipeline, own pose regression).
   - Two entries need volume and pages: `he2024probemounted`, `busam2018insideout`.
   - Suggest real references only when certain they exist, and mark them "verify".
3. **Supplementary material.** The draft refers to it several times (tracker distance trend, pooled S-new maps, further coverage views, US-only and fusion results). It does not exist yet.
4. **TBME checks.**
   - The abstract is about 248 words, structured Objective / Methods / Results / Conclusion / Significance.
   - Check the current TBME limits for abstract length and page count in the author guidelines.
   - Check the page count in Overleaf.
5. **Before submission.**
   - Remove the editing macros (`\tbd`, `\NUMQ`, `\NQ`) and the cyan abstract labels if TBME does not want them.
   - Update `\markboth` (it still says "VOL. XX, NO. XX, XXXX 2023").
   - Fill or remove the acknowledgment.
6. **Possible writing tasks:**
   - tighten the Introduction (long related-work paragraph);
   - cover letter;
   - highlights / significance statement;
   - response to reviewers later;
   - webpage text (the user wants 3D volume reconstructions shown visually there too).
7. **Future work worth mentioning** (Discussion):
   - An RGB-only probe camera, which is smaller and cheaper, and avoids depth failing on shiny surfaces. The network is already RGB-only; depth enters only the labels, Kabsch, ICP and the pose graph.
   - The cost of dropping depth at test time: PnP vs Kabsch anchors, S-val 5.1 vs 3.4 mm.
