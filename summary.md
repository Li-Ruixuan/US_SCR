# Markerless US probe tracking with one scene coordinate regression (SCR) network: results

Status 29 Oct 2026. Overview tables of all tests: 1.1. Builds on `rgbd-us` (`note_RPR.md` there). Run index: `runs/README.md`. Working notes and data guide: `note.md`. The earlier, chronological version of this summary (sections 3.1–3.20, all intermediate tables) is in git commit 870a144.

## 1. Bottom line

| question | answer | evidence |
|---|---|---|
| **Final system** | **One SCR network on every frame + Kabsch RANSAC on the measured depth + temporal smoothing.** No odometry, no hand-crafted features, no tracker at test time. Error at the US image: 2XX val 3.35, **3XX 1.85 (three seeds 1.85–2.12)**, 4XX A 5.14, B 5.77, C 5.63, D 9.63, E 6.25 mm | 3.1 |
| vs the classical system (SIFT anchors + SIFT odometry) | **Better where the room is well mapped** (3XX 1.85–2.12 vs 3.1 mm, every seed); **on par under the strict protocol** (map recorded before the sweeps: 2.98 vs 3.0 mm, smoother); **worse on new sessions with short room scans** (4XX 5.6–9.6 vs 3.4–6.3 mm, 1.4× on average) | 3.1, 4.3, 4.7 |
| Why worse on 4XX? | **Room-scan coverage:** the 4XX scans see 0–14 % of the sweep viewpoints (3XX 93–96 %). With 1–2 earlier sweeps added to the map (Polaris-labelled), SCR beats classical on 4XX too (A 2.3 vs 3.2, D 4.5 vs 5.8 mm). Labelling those sweeps with the system's own poses does not work (A 5.3 → 5.0 mm). **Pooling the room scans of the same day** (C's model also trained on A's and B's scans) helps without any labelling: C 5.63 → 3.98, D 9.63 → 8.46, E 6.25 → 5.92 mm (classical with the same pooled map: not run yet) | 4.3 |
| Is odometry needed? | **No.** On all 7 splits SCR alone, smoothed over 2 s, matches SCR + SIFT odometry in median (4XX mean 6.48 vs 6.54 mm) and is as smooth or smoother (step 0.82–1.68 vs 1.08–2.22 mm). Learned RPRNet odometry instead of SIFT is worse (+0.3–0.6 mm) | 3.1, 4.6 |
| Why did the first SCR fail (24–28 mm)? | **Undertrained,** not unable: same network and data, 2XX val 15.8 → 5.1 mm by the training fix alone; depth at test time (Kabsch) → 3.4 mm | 4.1 |
| SCR vs pose regression (RPR anchor network) | **SCR 3–6× more accurate on every split**, always solves (RPR: 37–93 % accepted) | 4.2, 5 |
| Strict protocol (map recorded before the sweeps) | **On par with classical:** single network 2.98 (1.18) vs classical system 3.0 (1.34) mm on run-315…317 with the map on room-301 only; with both room scans 1.83 vs 2.9. Part of the 3XX advantage comes from room-302, recorded after the sweeps | 4.7 |
| Is the 4XX gap distortion or offset? | **A rigid offset of each sweep:** after a rigid fit, the single network's volume shape is better than classical's on every split mean (2XX 3.04 vs 3.98, 3XX 1.57 vs 2.47, 3XX strict 2.26 vs 2.59, 4XX 3.17 vs 3.34 mm) | 4.8 |
| Can the US images help? | **No.** In-plane registration is worse than assuming no motion; speckle measures out-of-plane distance (0.3–0.4 mm) but the camera is 2–5× better between nearby frames; Li et al. (reproduced on its own data: 21.4 vs 22.8 mm published) is no better than zero motion on ours, fine-tuned worse | 6 |
| Model variants | Big head + clean labels adopted (lower p90 and rotation); viewpoint augmentation, full resolution, refined pose fit, multi-frame anchors: neutral or worse | 4.5 |

## 1.1 Overview tables

Five tables cover every test: A every system at the US image, B single-image pose methods, C coverage (what decides SCR vs classical), D where the error sits (local, shape, placement), E one row per test with its verdict. 4XX mean = mean of A–E. Details are in the sections given. As figures: `tools/tables/table_A.png` … `table_E.png` and `tools/tables/overview_tables.pdf` (`python tools/draw_overview_tables.py`; numbers copied from here, edit both together).

**Table A. Every system at the US image** (median mm per sweep, mean over sweeps; 3.1, 4.6)

| system | 2XX val | 3XX | 3XX strict | 4XX A | B | C | D | E | **4XX mean** | step 3XX / 4XX |
|---|---|---|---|---|---|---|---|---|---|---|
| classical odometry only (SIFT VO, each segment starts at the true pose) | 37.0 | 9.4 | 9.8 | 15.1 | 11.3 | 8.9 | 12.7 | 12.9 | 12.2 | |
| SCR every 0.25 s + RPRNet odometry, pose graph | | 3.2 | | 5.4 | | | 9.9 | | | 1.51 / |
| SCR anchors + SIFT odometry, pose graph (hybrid) | 4.2 | 2.6 | | 5.0 | 5.7 | 5.9 | 9.6 | 6.5 | 6.54 | 1.08 / 1.29 |
| **classical anchors + SIFT odometry** (classical system) | 4.2 | 3.1 | 3.0 | **4.2** | **3.4** | **4.9** | **6.3** | **5.0** | **4.76** | 1.09 / 1.28 |
| one SCR network, raw | 3.59 | 2.03 | 3.12 | 5.21 | 5.82 | 5.76 | 9.57 | 6.12 | 6.50 | 1.67 / 1.82 |
| **one SCR network, 2 s smoothing (ours)** | **3.35** | **1.85** | **2.98** | 5.14 | 5.77 | 5.63 | 9.63 | 6.25 | 6.48 | **0.93 / 1.15** |
| same, C / D / E model trained on all same-day room scans (A + B + C; A, B unchanged) | | | | 5.14 | 5.77 | **3.98** | 8.46 | 5.92 | 5.85 | / 1.09 |

- Odometry alone drifts (9–15 mm); every working system needs an absolute pose per frame or per second.
- The single network equals the hybrid on every split: SIFT odometry adds nothing once SCR runs on every frame; learned odometry is worse.
- Against classical: better on 3XX and 2XX, equal under the strict protocol, 1.4× worse on 4XX (1.2× with the pooled room scans, C now better than classical); always the smoothest.

**Table B. Pose from one image** (anchors: camera position median mm, rotation median, one frame per second; 4.1, 4.2)

| method | 2XX val | 3XX | 4XX mean | rotation 3XX / 4XX | frames solved |
|---|---|---|---|---|---|
| RPR anchor network (pose regression) | | 15.3 | 49.0 | | 3XX 93 %, 4XX 37–92 % |
| SCR, first recipe, PnP | 15.8 | | | | all |
| SCR v1 (fixed training), PnP | 5.1 | 2.5 | 11.1 | | all |
| SCR v1, Kabsch on depth | 3.4 | 2.0 | 6.4 | 0.19° / 0.56° | all |
| **SCR v2 (big head, clean labels), Kabsch** | **3.4** | **1.8** | 6.0 | **0.19°** / 0.49° | all |
| classical (SIFT to the room scan) | 5.2 | 2.6 | **5.3** | 0.34° / **0.38°** | all but A → C |

- The two big steps are training long enough (15.8 → 5.1) and using the measured depth at test time (PnP → Kabsch, 4XX 11.1 → 6.4); the head and labels mostly lower p90 and rotation.
- SCR is 8× more accurate than pose regression on both 3XX and 4XX.
- SCR vs classical follows the same pattern as Table A; on 4XX rotation is SCR's weak spot (0.49° vs 0.38°, about 0.2 mm at the US image per 0.1°).

**Table C. What decides SCR vs classical: room-scan coverage** (anchors in mm; US image where measured; 4.3, 4.4, 4.7)

| map (training data) → test | sweep viewpoints covered | SCR anchors | classical anchors | SCR / classical | SCR system | classical system |
|---|---|---|---|---|---|---|
| 3XX, both room scans | 93–96 % | **1.8** | 2.6 | 0.7 | **1.85** | 3.1 |
| 2XX val, both room scans | 75 % | **3.4** | 5.2 | 0.65 | **3.35** | 4.2 |
| 3XX strict, room-301 only (recorded before the sweeps) | fewer | 3.1 (v1) | **2.7** | 1.15 | 2.98 | 3.0 |
| 4XX, own room scans (40–90 s) | 0–14 % | 6.0 | **5.3** | 1.13 | 6.48 | **4.76** |
| A run-405…408, + run-401…404 (Polaris labels) | added views | **2.0** (from 5.6) | 3.7 (from 5.9) | 0.54 | **2.3** (hybrid) | 3.2 |
| D run-421, 423, 424, + run-418…420 (Polaris labels) | added views | **3.3** (from 8.6) | 4.7 (from 7.4) | 0.70 | **4.5** (hybrid) | 5.8 |
| C, D, E: C's room scans + A's and B's (same day, recorded earlier) | more room-scan views (4.8 min vs 1.3) | | | | C **3.98**, D 8.46, E 5.92 (from 5.63, 9.63, 6.25) | 4.9, 6.3, 5.0 with C's scans only; pooled map not run |
| same, labelled with the system's own poses | added views, wrong labels | A 5.0 (from 5.3), D 7.9 (from 9.0) | | | | |
| 2XX map → 3XX (a few objects moved) | outdated | **6.5** | 10.4 | 0.63 | | |
| A map → B (small rearrangement) | outdated | 14.0 | **7.9** | 1.8 | | |
| A map → C (large rearrangement) | outdated | **13.4** | 80.1 (21 % accepted) | | | |

- The SCR / classical ratio follows coverage: below 1 when the map covers the sweeps, about 1.1 when it does not.
- Adding real, correctly labelled views fixes it and SCR gains more from them than classical (A 5.6 → 2.0 vs 5.9 → 3.7).
- Room scans of the same day help too, although objects moved between A, B and C: C, D, E mean 7.17 → 6.12 mm, with no Polaris labels on sweeps.
- Views that are added but labelled wrongly (self-labels), or synthesised badly (point-splat renders, Table E), do not help: the training views must be correct.

**Table D. Where the error sits** (`runs/shape-final.md`, 3D pages; mm at the US image; 3.2, 4.8)

| split | system | absolute | shape (after a rigid fit of each sweep) | absolute − shape (placement) | out-of-plane error over 8 / 30 rows | 3D-page pixel error |
|---|---|---|---|---|---|---|
| 2XX val | **one SCR network** | **3.36** | **3.04** | 0.32 | 0.47 / 1.09 | **3.8** |
| 2XX val | classical system | 4.22 | 3.98 | 0.24 | 0.75 / 1.42 | 5.1 |
| 2XX val | classical odometry only | 36.98 | 14.26 | 22.72 | 0.69 / 1.44 | 29.4 |
| 3XX | **one SCR network** | **1.85** | **1.57** | 0.28 | 0.37 / 0.62 | **2.0** |
| 3XX | classical system | 3.11 | 2.47 | 0.64 | 0.29 / 0.62 | 3.2 |
| 3XX | classical odometry only | 9.43 | 6.23 | 3.20 | 0.28 / 0.54 | 10.1 |
| 3XX strict | **one SCR network** | 2.95 | **2.26** | 0.69 | 0.42 / 0.69 | 3.2 |
| 3XX strict | classical system | **2.91** | 2.59 | 0.32 | 0.34 / 0.72 | 3.2 |
| 3XX strict | classical odometry only | 9.77 | 6.14 | 3.63 | 0.33 / 0.62 | 10.4 |
| 4XX mean | **one SCR network** | 6.49 | **3.17** | 3.32 | 0.39 / 0.74 | 7.1 |
| 4XX mean | classical system | **4.75** | 3.34 | 1.41 | 0.39 / 0.76 | **5.2** |
| 4XX mean | classical odometry only | 12.19 | 6.66 | 5.53 | 0.41 / 0.86 | 12.5 |

- Between nearby frames all three are the same (0.3–0.4 mm over 8 rows): local motion is solved by any of them.
- The volume shape of the single network is better than classical's on every split mean: 2XX 3.04 vs 3.98, 3XX 1.57 vs 2.47, 3XX strict 2.26 vs 2.59, 4XX 3.17 vs 3.34 (A 2.92 vs 3.10, B 2.66 vs 2.47, C 2.96 vs 3.36, D 3.16 vs 3.61, E 4.16 vs 4.15).
- The whole 4XX gap is placement: each sweep is shifted rigidly in the room (3.3 mm vs 1.4 for classical). That is an anchoring error, which matches the coverage finding of Table C.

**Table E. Every test and its verdict** ("anchors" = camera position median, "US" = system at the US image, mm; rules fixed before each run on 2XX, or on 4XX A for coverage)

| area | test | measured on | result | verdict |
|---|---|---|---|---|
| training | fixed recipe, 15 → 120 epochs | 2XX anchors (PnP) | 15.8 → 5.1 | **adopted** |
| training | full resolution 720 × 1280 (30 epochs) | 2XX anchors | 6.3 → 7.3 | no |
| training | viewpoint augmentation (zoom, rotation) | 2XX anchors | 3.4 → 6.5 | no |
| training | big head + clean labels (v2) | 2XX p90, rotation | 8.7 → 7.3, 0.33° → 0.27° | **adopted** |
| training | frozen ImageNet encoder | 4XX A US | 5.14 → 5.24 | no |
| training | + rendered views (point splats) | 4XX A US | 5.14 → 4.98 | no (rule: ≥ 0.5 mm better) |
| training | frozen encoder + rendered views | 4XX A US | 5.14 → 5.51 | no |
| training | seeds 0 / 1 / 2 | 3XX US | 1.85 / 1.95 / 2.12 | noise ≈ 0.3 mm |
| training | 240 instead of 120 epochs | 4XX A US (fit) | 5.14 → 5.28 (fit 1.24 → 1.05 mm) | no |
| pose | pose regression (RPR) instead of SCR | 3XX / 4XX anchors | 15.3 / 49.0 vs 1.8 / 6.0 | **SCR** |
| pose | Kabsch on measured depth instead of PnP | 2XX anchors | 5.1 → 3.4 | **adopted** |
| pose | refined pose fit (noise weights; reprojection + depth) | 2XX anchors | 3.4 → 4.7 / 3.6 | no |
| pose | inlier gate ≥ 400 | all splits | trims tails on D, E, A → C | kept |
| pose | multi-frame anchors (3 / 5 frames) | 2XX US (hybrid) | 4.2 → 4.4 / 4.5 | no |
| time | SIFT odometry + pose graph vs one network | 4XX mean US | 6.54 vs 6.48 | **odometry dropped** |
| time | RPRNet (learned) odometry instead of SIFT | 3XX / A / D US | 0.3–0.6 mm worse | no |
| time | 2 s robust smoothing vs raw | 3XX US (step) | 2.03 (1.67) → 1.85 (0.93) | **adopted** |
| time | pose graph with zero-motion odometry | 3XX US | 2.0 → 4.9 | no |
| time | gate recovery (hybrid only) | run-404 US | 28.3 → 8.2 | kept for the hybrid |
| time | pose-graph anchor σ 11 / 5 / 3 mm | 2XX US | 4.4 / 4.4 / 4.5 | default kept |
| map | + earlier sweeps, Polaris labels | 4XX A / D anchors | 5.6 → 2.0 / 8.6 → 3.3 | works, needs Polaris |
| map | + same-day room scans (A, B scans for C, D, E) | 4XX C / D / E US | 5.63 / 9.63 / 6.25 → 3.98 / 8.46 / 5.92 | **adopted** (rule: mean ≥ 0.5 better; 7.17 → 6.12) |
| map | + earlier sweeps, labelled with own poses | 4XX A / D anchors | 5.3 → 5.0 / 9.0 → 7.9 | no |
| map | strict protocol (room-301 only) | 3XX run-315…317 US | 1.85 → 2.98 (classical 3.0) | report both |
| map | outdated map (previous session) | anchors | 2XX → 3XX 6.5; A → B 14.0; A → C 13.4 | re-scan per session |
| US | U1 in-plane registration (ECC) | 2XX, 10 rows | 1.91 vs 1.55 for zero motion | no |
| US | U2 speckle decorrelation → distance | all | 0.27–0.43 mm, magnitude only | no |
| US | U3 per-patch speckle vs camera | 3XX, 4 rows | 0.78 vs camera 0.19 mm | no |
| US | Li et al. reproduced on its own data | their test set | 21.4 vs 22.8 mm published | reproduced |
| US | Li et al. on our sweeps | 3XX / A / D | zero-shot 129; fine-tuned 75–125; scratch = zero motion | no |

**Conclusions from the five tables**

1. **Geometry beats regression.** Predicting room coordinates and solving the pose on the measured depth is what works (Table B); every learned shortcut (pose regression, learned odometry, US-only networks) is worse or no better than zero motion (Tables A, E).
2. **One network is enough.** With SCR on every frame and smoothing, odometry adds nothing (Table A), and the shape and local accuracy are classical-grade or better (Table D).
3. **Coverage is the limit.** SCR wins where the room scan covers the sweep viewpoints and loses when it does not (Table C). The 4XX loss is a rigid placement offset, not a worse volume (Table D).
4. **Only real, correctly placed training views close the gap.** Polaris-labelled sweeps do (A 5.6 → 2.0), and so do more room scans of the same day (C, D, E 7.17 → 6.12); self-labels, frozen features, more epochs and point-splat renders do not (Tables C, E). Next steps: longer room scans, or a realistic renderer.
5. **The US images carry no usable pose information** beyond what the camera gives (Table E, US rows).

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
| 4XX B | 5.77 (0.92) | 5.82 (1.76) | 5.7 (1.33) | **3.4** (1.32) |
| 4XX C | 5.63 (0.82) | 5.76 (1.48) | 5.9 (1.17) | **4.9** (1.19) |
| 4XX D | 9.63 (1.34) | 9.57 (1.92) | 9.6 (1.18) | **6.3** (1.19) |
| 4XX E | 6.25 (1.68) | 6.12 (2.19) | 6.5 (1.65) | **5.0** (1.57) |
| 3XX, seeds 1 / 2 | 1.95 (0.92) / 2.12 (0.93) | 2.11 / 2.20 | 2.7 / 2.7 (v1) | |
| 3XX strict (map room-301 only, run-315…317) | 2.98 (1.18) | 3.12 (1.94) | | 3.0 (1.34) |

- One network is enough: the rule (median equal to SCR + SIFT, step within 20 %) is met on all six test splits; same or better median, as smooth or smoother (2-row step 0.30–0.73 mm). 3XX: every sweep 1.4–2.1 mm; three seeds 1.85, 1.95, 2.12 (spread 0.27 mm), all below classical (3.1).
- Strict protocol: 2.98 vs 3.0 mm for classical (per sweep 3.7 / 2.4 / 2.9 vs 2.9 / 2.2 / 3.7), smoother (1.18 vs 1.34): on par, as the anchors were (4.7).
- 4XX: on average 6.48 mm vs 4.76 for classical (1.4×). Smoothing cannot remove a wrong-but-consistent error (D run-420, 421; E, where 6 % of the frames fail the gate, raw 6.12 vs smoothed 6.25): coverage decides 4XX.
- Caveat: offline smoothing (the 2 s window sees 1 s ahead); a causal version is not tested yet.

### 3.2 3D pages (`runs/volume3d/index.html`)

One page per sweep (`runs/volume3d/<split>/<run>.html`, open in a browser): the US volume compounded with the true poses and with the single network, the classical system and classical odometry only; mean pixel error over the compounded US images (the rgbd-us headline metric). The index lists every sweep.

| split | one SCR network | classical system | classical odometry only |
|---|---|---|---|
| 3XX | **2.0** | 3.2 | 10.1 |
| 4XX A | 5.4 | **4.4** | 14.5 |
| 4XX B | 5.8 | **3.7** | 11.1 |
| 4XX C | 6.6 | **5.3** | 9.8 |
| 4XX D | 10.4 | **7.2** | 13.1 |
| 4XX E | 7.1 | **5.2** | 13.8 |
| 2XX val | **3.8** | 5.1 | 29.4 |
| 3XX strict | 3.2 | 3.2 | 10.4 |

Same ranking as 3.1. Earlier pages of the hybrid system (SCR anchors + SIFT odometry; 3XX 2.7 vs 3.2 mm for classical, 4XX 5.3–10.5 vs 3.7–7.2) are in git commit 50ef6f5 (`runs/volume3d-final`).

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
- **Room scans of the same day pooled** (`v2pool-4XXC`: room-401…406, 8,671 frames, all recorded before the C sweeps; US image, 2 s smoothing): C 5.63 → **3.98**, D 9.63 → 8.46, E 6.25 → 5.92 mm (step 0.79 / 1.17 / 1.56). The rule fixed before the run (mean over C, D, E ≥ 0.5 mm better) is met: 7.17 → 6.12. C is now better than the classical system (4.9), D and E still worse (6.3, 5.0). Objects moved between A, B and C, yet the static parts of the room gain views. Not yet run: classical with the same pooled map (fair comparison), and B with A's scans.

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

**Training strategies against the coverage gap** (29 Oct; 4XX A as validation because 2XX is 75 % covered; rule fixed in advance: adopt if the single-network system on 4XX A is ≥ 0.5 mm better than v2, about twice the seed spread). US image, 2 s smoothing (step in brackets); fit = pose of training frames:

| model on 4XX A | US image | fit | decision |
|---|---|---|---|
| v2 (reference) | 5.14 (0.99) | 1.2 mm / 0.12° | |
| frozen ImageNet encoder, head only (`--freeze-encoder`) | 5.24 (0.97) | 3.7 mm / 0.23° | not adopted |
| + 0.5 rendered views per frame (`--render-views 0.5`: 1,946 views splatted from a 5 mm point cloud of the room scan, camera moved ≤ 150 mm, turned ≤ 20°) | 4.98 (0.98) | 1.6 mm / 0.13° | not adopted (−0.16 mm, within noise) |
| both | 5.51 (0.95) | 4.2 mm / 0.27° | not adopted |
| 240 instead of 120 epochs | 5.28 (0.99) | 1.05 mm / 0.08° | not adopted: fits the scan better, generalises no better |

Frozen features fit the room worse and do not generalise better. Rendered views help slightly, but the point-splat renders are blocky with see-through holes (`runs/v2rv-4XXA/render_preview.jpg`): a large appearance gap to real images. A better renderer (TSDF mesh or Gaussian splats) is the open question; with these renders, coverage is not bought by synthesis.

### 4.6 Without SIFT odometry (`runs/sys-learned-*`)

Median at the US image (step in brackets). SCR every 0.25 s with RPRNet odometry (learned) and a pose graph: 3XX 3.2 (1.51), A 5.4 (1.19), D 9.9 (1.21), i.e. 0.3–0.6 mm worse than SCR + SIFT; with anchors every 1 s RPRNet drifts too much (3XX 5.0). SCR every 0.25 s alone, raw: 2.0 (1.69), 5.2 (1.81), 9.7 (1.88); a pose graph with zero-motion odometry hurts it (3XX 4.9). Hence the robust smoother of 3.1.

### 4.7 Strict protocol for 3XX (map recorded before the sweeps)

room-301 was recorded between run-314 and run-315, room-302 after all sweeps. Map on room-301 only, test run-315…317 (anchors; classical system at the US image):

| map | SCR anchors (v1) | classical anchors | classical system |
|---|---|---|---|
| room-301 + room-302 | **1.8**, 0.20° | 2.5, 0.29° | 2.9 |
| room-301 only (strict) | 3.1 / 6.1, **0.26°** | **2.7 / 6.1**, 0.32° | 3.0 |

SCR loses more from the shorter map (coverage again). The single-network system under this protocol (`v2-3XX-room301`, `track-3XX-room301`): 2.98 mm at the US image vs 3.0 for the classical system, on par (3.1).

### 4.8 Shape of the reconstruction (`runs/shape-final.md`, single network vs classical)

Error at the US image after the best rigid fit of each whole sweep (the volume's distortion, without its placement in the room), absolute in brackets. Single network: 2XX **3.04** (3.36); 3XX **1.57** (1.85); 3XX strict **2.26** (2.95); 4XX A 2.92, B 2.66, C 2.96, D 3.16, E 4.16, mean **3.17** (6.49). Classical system: 2XX 3.98 (4.22); 3XX 2.47 (3.11); 3XX strict 2.59 (2.91); 4XX 3.10, 2.47, 3.36, 3.61, 4.15, mean 3.34 (4.75). Odometry only: 2XX 14.26, 3XX 6.23, 3XX strict 6.14, 4XX 6.66. The single network's 4XX error is a rigid offset of each whole sweep; its shape is as good as classical's or better (Table D). The earlier hybrid (SCR anchors + SIFT) gave 3XX 2.1, 4XX 3.5. Caveat: the metric was introduced after the 4XX gap was known, so report it next to the absolute error.

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
3. **3XX room scans partly recorded after the sweeps:** with the map recorded before the sweeps SCR is on par with classical, not better (4.7); report both numbers.
4. **Small test sets, one room, two subjects;** seed spread measured on 3XX only (1.85–2.12 mm).
5. **Offline smoothing;** causal (real-time) version untested.
6. The inlier gate was chosen after seeing the test splits (no effect on system results).
7. Hand–eye calibration (3.5 mm board-corner error) enters labels and ground truth.

## 8. Open tasks

| priority | task | needs |
|---|---|---|
| 1 | causal smoothing (real time) | code, CPU |
| 2 | pooled room scans: classical with the same map (C, D, E), B with A's scans, shape of the pooled models | run |
| 3 | confidence head + weighted Kabsch, trained end to end | code, training |
| 4 | rendered views with a realistic renderer (TSDF mesh / Gaussian splats); point-splat renders gave −0.16 mm on 4XX A (4.5) | code, training |

Files and commands: `README.md`.
