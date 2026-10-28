# Markerless US probe tracking with one scene coordinate regression (SCR) network: results

Status 28 Oct 2026. Builds on `rgbd-us` (`note_RPR.md` there). Run index: `runs/README.md`. Working notes and data guide: `note.md`. The earlier, chronological version of this summary (sections 3.1–3.20, all intermediate tables) is in git commit 870a144.

## 1. Bottom line

| question | answer | evidence |
|---|---|---|
| **Final system** | **One SCR network on every frame + Kabsch RANSAC on the measured depth + temporal smoothing.** No odometry, no hand-crafted features, no tracker at test time. Error at the US image: 2XX val 3.35, **3XX 1.85**, 4XX A 5.14, D 9.63 mm (B, C, E pending) | 3.1 |
| vs the classical system (SIFT anchors + SIFT odometry) | **Better where the room is well mapped** (3XX 1.85 vs 3.1 mm); **worse on new sessions with short room scans** (4XX A 5.1 vs 4.2, D 9.6 vs 6.3 mm) | 3.1, 4.3 |
| Why worse on 4XX? | **Room-scan coverage:** the 4XX scans see 0–14 % of the sweep viewpoints (3XX 93–96 %). With 1–2 earlier sweeps added to the map (Polaris-labelled), SCR beats classical on 4XX too (A 2.3 vs 3.2, D 4.5 vs 5.8 mm). Labelling those sweeps with the system's own poses does not work (A 5.3 → 5.0 mm) | 4.3 |
| Is odometry needed? | **No.** SCR alone gives the same median as SCR + SIFT odometry; smoothing over 2 s makes it as smooth or smoother (step 0.93–1.34 vs 1.08–2.22 mm). Learned RPRNet odometry instead of SIFT is worse (+0.3–0.6 mm) | 3.1, 4.6 |
| Why did the first SCR fail (24–28 mm)? | **Undertrained,** not unable: same network and data, 2XX val 15.8 → 5.1 mm by the training fix alone; depth at test time (Kabsch) → 3.4 mm | 4.1 |
| SCR vs pose regression (RPR anchor network) | **SCR 3–6× more accurate on every split**, always solves (RPR: 37–93 % accepted) | 4.2, 5 |
| Strict protocol (map recorded before the sweeps) | Anchors on par with classical on 3XX (3.1 vs 2.7 mm, better rotation), not better: part of the 3XX advantage comes from room-302, recorded after the sweeps. Single-network run pending | 4.7 |
| Is the 4XX gap distortion or offset? | **Mostly a rigid offset of each sweep:** after a rigid fit, SCR and classical give the same volume shape on 4XX (3.5 vs 3.3 mm) | 4.8 |
| Can the US images help? | **No.** In-plane registration is worse than assuming no motion; speckle measures out-of-plane distance (0.3–0.4 mm) but the camera is 2–5× better between nearby frames; Li et al. (reproduced on its own data: 21.4 vs 22.8 mm published) is no better than zero motion on ours, fine-tuned worse | 6 |
| Model variants | Big head + clean labels adopted (lower p90 and rotation); viewpoint augmentation, full resolution, refined pose fit, multi-frame anchors: neutral or worse | 4.5 |

## 2. Setup

**Hardware.** A probe-mounted RealSense D435i (colour 1280 × 720, depth aligned) looks at the room; an NDI Polaris marker on the probe gives ground truth (~0.25 mm). Target: ~2 mm at the US image, ~16 cm from the camera (1° ≈ 1.6 mm at the image bottom).

**Data.**

| collection | room scans (map) | sweeps (test) | role |
|---|---|---|---|
| 2XX (9 Oct) | room-201, 202: 3.0 min, 5,366 frames | run-205, run-211 | **validation: every setting is chosen here** |
| 3XX (9 Oct) | room-301, 302: 2.0 min, 3,356 frames | run-313…317 | clean test: same room, a few small objects moved |
| 4XX A (14 Oct) | room-401 (90 s), 402 (40 s) | run-401…408 | new session |
| 4XX B | room-403, 404 (40 s each) | run-409…412 | small rearrangement |
| 4XX C | room-405, 406 (40 s each) | run-413…416 | large rearrangement |
| 4XX D, E | C's scans | run-418…421, 423, 424; run-425…428 | second subject; occlusion |

**Protocol.** One model per session, trained on its room scans only (Polaris poses), tested on its sweeps. Anchor accuracy: camera position / rotation error against Polaris, one frame per second, mean of per-sweep medians / p90. System accuracy: **median error at the US image** (5 points via the US calibration) per sweep, mean over sweeps; **step-to-step error** = mean change of the error vector over 8 rows (0.27 s). Rules for adopting a change are fixed before the run and decided on 2XX; tests only report. Run-to-run noise: ~1 mm on 2XX (2 sweeps), ~0.3 mm on 3XX (seeds).

**Final model (v2, `scr_anchor.py train --head big --label-max-depth 2000 --drop-depth-edges`).**

| | first SCR (`rgbd-us/scr.py`) | **v2** |
|---|---|---|
| network | RGB 3 × 360 × 640 → EfficientNet-B0 (ImageNet), stride-8 (40 ch) + upsampled stride-16 (112 ch) features → 1×1 head 152→256→256→256→3 (0.17 M) → room coordinate per cell, 45 × 80 | same encoder; **big head**: 1×1 152→512, 4 residual blocks (512), 512→3 (2.18 M), fp32 |
| labels | room-scan depth at each cell centre, back-projected with the Polaris pose | same, **depth 0.1–2 m only, none on depth edges** |
| training | every 2nd frame, Huber (50 mm knee), OneCycle, 15 epochs, fp16 head | **every frame, 3D distance, flat lr 60 % then cosine, 120 epochs**; AdamW, head lr 1e-3, encoder 1e-4, batch 8; 20–50 min on an RTX A4500 |
| pose | PnP-RANSAC, 10 px | **Kabsch RANSAC on the measured depth**: 256 hypotheses, 20 mm, cells < 2 m, 3 refits; frame used only with ≥ 400 inliers |

## 3. Final system

### 3.1 One network on every frame (`scr_anchor.py track`, `runs/track-*`)

SCR + Kabsch on every 2nd usable row (15 Hz), no odometry, no Polaris start pose; a robust local fit over time (window chosen on 2XX by the rule "lowest median with a step error at most SCR + SIFT's": **2 s**; offline, as the pose graph). Median error at the US image (mm), step-to-step error in brackets.

| split | **SCR alone, smoothed 2 s** | SCR alone, raw | SCR anchors + SIFT odometry, pose graph | classical anchors + SIFT odometry |
|---|---|---|---|---|
| 2XX val | **3.35** (1.20) | 3.59 (2.72) | 4.2 (2.22) | 4.2 (2.27) |
| 3XX | **1.85** (0.93) | 2.03 (1.67) | 2.6 (1.08) | 3.1 (1.09) |
| 4XX A | 5.14 (0.99) | 5.21 (1.75) | 5.0 (1.10) | **4.2** (1.13) |
| 4XX B | pending | | 5.7 (1.33) | **3.4** (1.32) |
| 4XX C | pending | | 5.9 (1.17) | **4.9** (1.19) |
| 4XX D | 9.63 (1.34) | 9.57 (1.92) | 9.6 (1.18) | **6.3** (1.19) |
| 4XX E | pending | | 6.5 (1.65) | **5.0** (1.57) |

- One network is enough: same or better median than with SIFT odometry, as smooth or smoother (2-row step 0.35–0.60 mm). 3XX: every sweep 1.4–2.1 mm.
- Smoothing cannot remove a wrong-but-consistent error (4XX D run-420, 421 slightly worse after smoothing): coverage decides 4XX.
- Caveat: offline smoothing (the 2 s window sees 1 s ahead); a causal version is not tested yet.

### 3.2 3D pages of the earlier hybrid system (`runs/volume3d-final/`)

Mean pixel error over the compounded US images (rgbd-us headline metric), SCR anchors + SIFT odometry vs classical + SIFT odometry, every sweep: 3XX **2.7** vs 3.2 (SCR better on all 5 sweeps); A 5.3 vs **4.4**, B 6.0 vs **3.7**, C 6.9 vs **5.3**, D 10.5 vs **7.2**, E 7.8 vs **5.2** mm (SCR better on 3 of 26 4XX sweeps). Pages of the single-network system: not built yet.

## 4. Studies behind the design

### 4.1 Training fixes (2XX validation, PnP unless noted)

| model | anchors (median / p90) | training-frame pose |
|---|---|---|
| first SCR recipe | 15.8 / 31.3 | 13.2 mm |
| fixed recipe, 30 / 60 / 120 epochs | 6.3 / 5.4 / **5.1** | 5.6 / 4.0 / 2.7 mm |
| 120 epochs + **Kabsch** (depth at test time) | **3.4 / 8.7**, 0.33° | |
| full resolution 720 × 1280 (30 epochs) | 7.3 / 14.5 | 6.6 mm |
| classical anchors | 5.2 / 11.9, 0.33° | |

Beyond ~60 epochs validation stops improving while the fit keeps improving: the limit becomes generalisation. The coordinate error (~12 mm) is scatter that RANSAC averages into 2–5 mm poses.

### 4.2 Anchor accuracy (Kabsch, one frame per second)

| split | **SCR v2** | SCR v1 (small head) | SCR v1 + PnP | classical anchors | RPR anchor network |
|---|---|---|---|---|---|
| 3XX | **1.8 / 3.4, 0.19°** | 2.0 / 3.3, 0.19° | 2.5 / 5.4 | 2.6 / 6.9, 0.34° | 15.3 (93 %) |
| 4XX A | 5.4 / 8.9, 0.45° | 5.9 / 10.1, 0.48° | 9.9 / 17.6 | **5.3 / 10.1, 0.48°** | 40.3 (73 %) |
| 4XX B | 5.6 / 8.0, 0.35° | 5.9 / 9.2, 0.40° | 8.6 / 17.8 | **3.2 / 5.0, 0.25°** | 25.4 (92 %) |
| 4XX C | **4.8 / 9.9**, 0.59° | 5.2 / 10.1, 0.74° | 11.2 / 17.0 | 5.9 / 11.1, 0.39° | 67.0 (66 %) |
| 4XX D | 8.6 / 14.5, 0.64° | 9.3 / 18.9, 0.73° | 15.4 / 29.2 | **7.1 / 18.3, 0.41°** | 54.5 (58 %) |
| 4XX E | 5.7 / 9.7, 0.40° | 5.9 / 13.9, 0.46° | 10.2 / 20.5 | **5.2 / 8.5, 0.35°** | 57.9 (37 %) |

Seeds (v1): 3XX 1.9–2.2 mm over 3 seeds, 4XX A 5.8–5.9 mm. Rotation is SCR's weak spot on 4XX, and it dominates the error at the US image there.

### 4.3 Coverage and map extension

- **Coverage** (a room-scan pose within 30 mm and 10°): covered frames 4.1 mm, uncovered 13.4 mm (all splits pooled, v1 + PnP); 4XX A grows from 8.1 to 13.9 mm as the nearest room-scan pose goes from < 30 to 60–100 mm.
- **Map + earlier sweeps of the same block (Polaris labels)**, tested on the later sweeps (anchors; US image with the pose graph):

| block, test sweeps | map | SCR anchors | classical anchors | SCR system | classical system |
|---|---|---|---|---|---|
| A, run-405…408 | room scans | 5.6, 0.47° | 5.9, 0.48° | 5.0 | **4.5** |
| A | + run-401…404 (one sweep gives most of it) | **2.0 / 4.6, 0.20°** | 3.7 / 7.0, 0.36° | **2.3** | 3.2 |
| D, run-421, 423, 424 | C's room scans | 8.6, 0.76° | 7.4, 0.46° | 10.2 | **7.2** |
| D | + run-418…420 | **3.3 / 7.7, 0.27°** | 4.7 / 14.6, 0.35° | **4.5** | 5.8 |

- **Same, labelled with the system's own poses (no Polaris):** A 5.3 → 5.0, D 9.0 → 7.9 mm (Polaris labels: 1.9, 3.1). The network learns the label errors (5–14 mm); map extension is only as good as the poses of the added views.

### 4.4 Outdated room scans (map of one session, sweeps of a later one; anchors)

| map → sweeps | SCR + Kabsch | SCR + PnP | classical | RPR |
|---|---|---|---|---|
| 2XX → 3XX | **6.5 / 11.8** | 21.2 / 47.8 | 10.4 / 20.3 | 39.8 |
| A → B (small change) | 14.0 / 25.4 | 31.7 / 47.3 | **7.9 / 12.9** | 81.6 |
| A → C (large change) | **13.4** / 113.0 (gated: 8.2 / 16.6, 49 % kept) | 47.4 / 65.2 | 80.1 (21 % accepted) | 51.8 |

### 4.5 Model and solver variants (2XX validation decides)

| variant | result | decision |
|---|---|---|
| big head (2.18 M) + clean labels | median same, p90 8.7 → 7.3 / 9.4 → 6.9, rotation 0.33 → 0.27° / 0.37 → 0.28° (2 seeds); every test split slightly better (4.2) | **adopted (v2)** |
| viewpoint augmentation (zoom 0.67–1.5, ±15°) | 2XX 3.4 → 6.5 mm; 4XX A 5.9 → 5.1 (noise) | not adopted |
| refined pose fit (depth-noise weights; joint reprojection + depth) | 3.4 → 4.7 / 3.6 mm | not adopted |
| multi-frame anchors (3, 5 frames pooled via odometry) | US image 4.2 → 4.4 / 4.5 mm | not adopted |
| inlier gate ≥ 400 | unchanged on unchanged rooms; trims tails on D, E, A → C; no effect on the system | kept (chosen after seeing the tests: report ungated too) |
| gate recovery (accept again after 3 agreeing rejected anchors) | fixed run-404 in the hybrid system (28.3 → 8.2 mm) | kept for the hybrid system |
| pose-graph anchor σ (11 / 5 / 3 mm) | 4.4 / 4.4 / 4.5 mm | default kept |

### 4.6 Without SIFT odometry (`runs/sys-learned-*`)

Median at the US image (step in brackets). SCR every 0.25 s with RPRNet odometry (learned) and a pose graph: 3XX 3.2 (1.51), A 5.4 (1.19), D 9.9 (1.21), i.e. 0.3–0.6 mm worse than SCR + SIFT; with anchors every 1 s RPRNet drifts too much (3XX 5.0). SCR every 0.25 s alone, raw: 2.0 (1.69), 5.2 (1.81), 9.7 (1.88); a pose graph with zero-motion odometry hurts it (3XX 4.9). Hence the robust smoother of 3.1.

### 4.7 Strict protocol for 3XX (map recorded before the sweeps)

room-301 was recorded between run-314 and run-315, room-302 after all sweeps. Map on room-301 only, test run-315…317 (anchors; classical system at the US image):

| map | SCR anchors (v1) | classical anchors | classical system |
|---|---|---|---|
| room-301 + room-302 | **1.8**, 0.20° | 2.5, 0.29° | 2.9 |
| room-301 only (strict) | 3.1 / 6.1, **0.26°** | **2.7 / 6.1**, 0.32° | 3.0 |

SCR loses more from the shorter map (coverage again). The single-network system under this protocol is pending (`v2-3XX-room301`).

### 4.8 Shape of the reconstruction (`runs/shape-final.md`, hybrid systems)

Error at the US image after the best rigid fit of each whole sweep (the volume's distortion, without its placement in the room), absolute in brackets: 3XX SCR **2.1** (2.5) vs classical 2.5 (3.1); 4XX mean SCR 3.5 vs classical 3.3 (absolute 1.2–1.7× worse). SCR's 4XX error is mostly a rigid offset of a whole sweep (consecutive anchor errors correlate 0.6–0.8). Caveat: metric introduced after the 4XX gap was known; report it next to the absolute error.

## 5. Why SCR beats pose regression

| | RPR anchor network | SCR |
|---|---|---|
| output | one 6-DoF pose per image pair | ~3,600 room coordinates per image |
| pose computed by | the network | geometry (RANSAC + Kabsch on measured depth) |
| must learn | a general "image pair → motion" rule, valid across sessions | one room: "this patch is at (x, y, z)" |
| wrong content (hands, moved objects) | mixed into the pose | rejected as outliers |
| anchor error | 15 mm (3XX), 25–67 mm (4XX) | 1.8 mm (3XX), 5–9 mm (4XX) |

Precision comes from averaging thousands of 7–12 mm coordinate predictions in a rigid fit; geometry (intrinsics, depth, rigid transform) is left to an exact solver. Neither method generalises to unseen viewpoints; SCR is retrained per room, where memorising the room is the job.

## 6. US images (`tools/us_analysis.py`, `tools/li_baseline.py`; all negative)

| test | result |
|---|---|
| U1: in-plane registration (ECC) of frames 1–10 apart | worse than assuming no in-plane motion (e.g. 2XX k = 10: 1.91 vs 1.55 mm); the probe moves out of plane |
| U2: speckle decorrelation vs out-of-plane distance | same curve in every session and both subjects; distance from a 2XX curve 0.27–0.43 mm median error; magnitude only |
| U3: per-patch speckle (shift + 2 tilts) against the camera system | camera 2–5× better between nearby frames (3XX 0.07 / 0.19 / 0.24 vs 0.19 / 0.78 / 1.83 mm at 1 / 4 / 8 rows); no fusion helps |
| Li et al. (TBME 2024) reproduced on its own data | 21.4 ± 11.2 mm accumulated error vs 22.8 ± 17.5 published (zero motion 73.1) |
| Li et al. on our sweeps (accumulated error, 3XX / A / D) | zero-shot 129 (3XX); fine-tuned 75 / 125 / 82; from scratch 56 / 49 / 52 = zero motion 58 / 49 / 53; camera 15–30× better at 1 s |

The remaining error is long-range (sweep-scale), which speckle cannot see; a learned sensorless network learns its training protocol, not our motion.

## 7. Limitations

1. **Coverage:** SCR does not extrapolate to viewpoints the room scan missed; classical anchors cope better (4XX).
2. **Polaris-built maps:** the room-scan poses come from Polaris; in deployment they would come from SLAM / ACE0-style reconstruction (untested).
3. **3XX room scans partly recorded after the sweeps** (4.7); the strict number is pending for the final system.
4. **Small test sets, one room, two subjects;** one seed for the final system (seed spread pending).
5. **Offline smoothing;** causal (real-time) version untested.
6. The inlier gate was chosen after seeing the test splits (no effect on system results).
7. Hand–eye calibration (3.5 mm board-corner error) enters labels and ground truth.

## 8. Open tasks

| priority | task | needs |
|---|---|---|
| 1 | single-network system on 4XX B, C, E | commands only |
| 2 | strict protocol (`v2-3XX-room301`) and seed spread (`v2-3XX-seed1/2`) for the final system | 3 trainings |
| 3 | causal smoothing (real time) | code, CPU |
| 4 | 3D pages of the single-network system | code |
| 5 | confidence head + weighted Kabsch, trained end to end | code, training |
| 6 | rendered views from the room reconstruction for training (coverage) | code, training |

Files and commands: `README.md`.
