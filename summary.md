# Scene coordinate regression (SCR) anchors for markerless US probe tracking: summary of all tests

Status 23 Oct 2026. Project: `US_SCR` (this repo), building on `rgbd-us` (`note_RPR.md`). Working notes with the full history: `note.md`.

## 1. Bottom line

| question | answer | strength of evidence |
|---|---|---|
| Why did the first SCR underfit? | It was undertrained, not unable to learn: same network and data, 2XX validation 15.8 → 5.1 mm by fixing the training alone | strong (single change, large effect) |
| Does depth help? | Yes: 3D–3D RANSAC (Kabsch) on the measured depth instead of PnP gives a further 20–55 % on every split (2XX validation 5.1 → 3.4 mm) | strong (every split) |
| Unchanged room, good room-scan coverage (3XX)? | **On par with or better than classical, depending on the map:** with both room scans SCR is the best anchor and system (anchors 2.0 vs 2.6 mm, 0.19 vs 0.34°; US image 2.6–2.7 vs 3.1 mm over three seeds); with only the room scan recorded before the sweeps it is on par (anchors 3.1 vs 2.7 mm, same p90, better rotation) | **weakened by the strict-protocol check:** with the map recorded before the sweeps (room-301 only) SCR is on par with classical (3.1 vs 2.7 mm, same p90, better rotation), not better; the advantage with both scans (three seeds, system 2.6–2.7 vs 3.1 mm) depends partly on room-302, recorded after the sweeps (3.14) |
| New session, short room scans (4XX)? | **Classical is still 1.3–1.8× better at the US image** (median, every segment started from an anchor: SCR 5.5–10.3 vs 3.4–6.3 mm); the big head + clean labels lower the anchor error a little on every split but do not close the gap | strong |
| Why worse on 4XX? | **Room-scan coverage.** The short 4XX room scans cover 0–14 % of the sweep viewpoints. Adding 2–4 earlier sweeps to the map (Polaris-labelled) brings 4XX A to 1.9 mm / 0.22° and makes SCR the better system on both blocks tested (US image A 2.3 vs 3.2, D 4.5 vs 5.8 mm, classical given the same keyframes); the rotation gap disappears too | strong (covered vs uncovered 4.1 vs 13.4 mm; extended maps on two blocks, fair comparison) |
| Can the map be extended without a tracker? | **Not yet:** labelling the extra sweeps with the system's own poses (5–14 mm off) recovers almost none of the gain (A 5.3 → 5.0, D 9.0 → 7.9 mm); the network learns the label errors | strong for this labelling; more accurate labels (e.g. refined against the room scan) untested |
| Outdated room scan? | SCR + Kabsch beats classical on 2XX → 3XX (6.5 vs 10.4 mm) and the large change A → C (13.4 vs 80 mm), loses on the small change A → B (14.0 vs 7.9 mm) | moderate (one pair each) |
| SCR vs the RPR anchor network? | **SCR is 3–6× more accurate on every split** and always solves (RPR: 37–93 % accepted) | strong |
| Bigger head, cleaner labels, refined pose fit, viewpoint augmentation, full resolution? | Big head + clean labels: lower p90 and rotation on 2XX for both seeds, median unchanged — adopted, effect on the test splits not yet measured; nothing on extended maps. Refined pose fit, viewpoint augmentation and full resolution: neutral or worse | moderate |
| Is the classical odometry needed? | Only for smoothness: SCR anchors every 0.25 s without odometry give the same median error at the US image but 1.4–1.7× larger step-to-step error | moderate (three splits) |
| Can US images help? | Not for in-plane motion (registration worse than assuming none); yes for out-of-plane distance (speckle decorrelation, 0.3–0.4 mm median, transfers across sessions and subjects) — not yet in the system | strong for the diagnostics, untested in the system |

## 2. Setup

### 2.1 System
A probe-mounted RealSense D435i (colour 1280 × 720) looks at the room; an NDI Polaris marker on the probe gives ground truth (~0.25 mm). The pose of every US frame comes from **odometry** between frames plus **anchors** (absolute poses against a room scan recorded before the exam), combined in an offline **pose graph**. Target: ~2 mm at the US image, ~16 cm from the camera (1° of rotation ≈ 1.6 mm at the image bottom). SCR replaces the anchors.

### 2.2 Data

| collection | room scans (map) | sweeps (test) | role |
|---|---|---|---|
| 2XX (9 Oct) | room-201, 202: 3.0 min, 5,366 frames | run-205, run-211 | **validation: all settings chosen here** |
| 3XX (9 Oct) | room-301, 302: 2.0 min, 3,356 frames | run-313…317 | clean test: same room as 2XX, a few small objects moved |
| 4XX A (14 Oct) | room-401 (90 s), 402 (40 s): 3,893 frames | run-401…408 | new session |
| 4XX B | room-403, 404 (40 s each): 2,381 frames | run-409…412 | small rearrangement |
| 4XX C | room-405, 406 (40 s each): 2,397 frames | run-413…416 | large rearrangement |
| 4XX D | C's scans | run-418…421, 423, 424 | second subject |
| 4XX E | C's scans | run-425…428 | occlusion (arm in view) |

Room-scan coverage of the sweep viewpoints (a room-scan pose within 30 mm and 10°): 3XX 93–96 %, 2XX validation 75 %, 4XX 0–14 %. 1XX is not used (broken depth).

### 2.3 Protocol (identical to `rgbd-us/scr.py eval`)
- Map on a session's **room scans only**; test on its sweeps, **one frame every 30 usable rows** (≈ 1 s; Polaris pose, probe on the skin, US frame and depth present).
- Anchor accuracy: camera position error (mm) and rotation error (°) against Polaris, median and p90, share solved. Tables give the **mean of per-sweep medians** (as rgbd-us); SCR p90 is pooled over frames, classical p90 is the mean of per-sweep p90s.
- Full system: rgbd-us `anchoring.py` (classical odometry, an anchor every 1 s, pose graph), error at the US image: **median** per sweep (anchoring tables) and **mean pixel error over the compounded US images** (3D pages, the metric of rgbd-us's headline table).
- **Settings are chosen on 2XX validation only**; 3XX and 4XX only report. Exceptions are listed in section 6.
- Run-to-run noise on 2XX validation (seed repeat): **≈ 1 mm**.

### 2.4 Model and training (final recipe "v1")

| | first SCR (`rgbd-us/scr.py`) | **v1** (`scr_anchor.py`) |
|---|---|---|
| network | RGB 360 × 640 → ImageNet EfficientNet-B0 to stride 16; stride-8 + stride-16 features → 1×1-conv head 152 → 256 → 256 → 256 → 3 (0.17 M parameters) → room coordinate per cell of a 45 × 80 grid | same, unchanged |
| training data | session room scans, every 2nd frame | session room scans, all frames |
| targets | room-scan depth at each cell centre, back-projected with the Polaris pose | same |
| loss | Huber on the 3D error, 50 mm knee | 3D distance |
| schedule | OneCycle, 15 epochs (2XX: 5,025 steps) | flat lr for 60 %, then cosine to 0; 120 epochs (2XX: 80,400 steps) |
| head output | fp16 (autocast) | fp32 |
| optimiser | AdamW, head lr 1e-3, encoder lr 1e-4, batch 8 | same |
| pose | PnP-RANSAC, 10 px, ≥ 30 inliers | **Kabsch: 3D–3D RANSAC between the measured depth and the predicted coordinates, 20 mm, cells < 2 m, ≥ 30 inliers** |
| gate in the full system | ≥ 30 inliers | ≥ 400 Kabsch inliers |
| training time (training PC, RTX A4500) | ~15–20 min | 3XX 24 min, 4XX 18–28 min, 2XX 52 min |
| time per frame | ~10 ms | PnP ~10 ms, Kabsch 50–75 ms (numpy) |

## 3. Results

### 3.1 Training fixes (2XX validation, PnP)

| run | change | anchor error mm (median / p90) | rotation ° | fit check on training frames: coordinates (after rigid fit) | pose of training frames |
|---|---|---|---|---|---|
| `s1-base-2XX` | first SCR recipe | 15.8 / 31.3 | 0.55 | 28.0 (26.7) mm | 13.2 mm |
| `s1-2XX` | S1 recipe, 30 epochs | 6.3 / 13.1 | 0.34 | 14.5 (13.7) | 5.6 |
| `s1-e60-2XX` | 60 epochs | 5.4 / 11.3 | 0.26 | 13.0 (12.3) | 4.0 |
| `s1-e60-seed1-2XX` | 60 epochs, seed 1 | 6.3 / 12.9 | 0.31 | 12.7 (11.9) | 3.8 |
| **`s1-e120-2XX`** | **120 epochs (v1)** | **5.1 / 11.3** | 0.31 | 11.5 (11.3) | 2.7 |
| `s3-full-2XX` | 720 × 1280 input, 30 epochs | 7.3 / 14.5 | 0.33 | 15.7 (14.8) | 6.6 |
| classical anchors | | 5.2 / 11.9 | 0.33 | | |

- The training fix alone removed most of the gap (15.8 → 5.1 mm). Beyond ~60 epochs validation stops improving while the training frames keep improving (5.6 → 4.0 → 2.7 mm): the limit becomes generalisation.
- Removing the best rigid fit barely changes the coordinate error: the error is scatter that RANSAC averages, not a per-frame offset; ~12 mm coordinates give 3–5 mm poses.
- Full resolution is worse at equal steps despite 4× the correspondences (9,573 vs 2,610 inliers): neighbouring cells make correlated errors.

### 3.2 Anchor accuracy on all splits

Mean of per-sweep medians / p90 (mm), rotation median; SCR = v1 recipe trained on each session's room scans (`runs/v1-*`, 2XX: `s1-e120-2XX`).

| split | **SCR v1 + Kabsch** | SCR v1 + PnP | classical anchors | RPR anchor network (adapted) | first SCR |
|---|---|---|---|---|---|
| 2XX val | **3.4 / 8.7, 0.33°** | 5.1 / 11.3, 0.31° | 5.2 / 11.9, 0.33° | — | 15.8 / 31.3 |
| 3XX | **2.0 / 3.3, 0.19°** | 2.5 / 5.4, 0.18° | 2.6 / 6.9, 0.34° | 15.3 / 27.5 (93 % accepted) | 9.8 / 22.1 |
| 4XX A | 5.9 / 10.1, 0.48° | 9.9 / 17.6, 0.60° | **5.3 / 10.1, 0.48°** | 40.3 / 78.2 (73 %) | 17.7 |
| 4XX B | 5.9 / 9.2, 0.40° | 8.6 / 17.8, 0.48° | **3.2 / 5.0, 0.25°** | 25.4 / 51.5 (92 %) | 16.0 |
| 4XX C | **5.2 / 10.1**, 0.74° | 11.2 / 17.0, 0.96° | 5.9 / 11.1, 0.39° | 67.0 / 120.5 (66 %) | 21.8 |
| 4XX D | 9.3 / 18.9, 0.73° | 15.4 / 29.2, 0.98° | **7.1 / 18.3, 0.41°** (98 %) | 54.5 / 89.2 (58 %) | 26.0 |
| 4XX E | 5.9 / 13.9, 0.46° (99 % solved) | 10.2 / 20.5, 0.56° | **5.2 / 8.5, 0.35°** | 57.9 / 124.6 (37 %) | 22.1 |

SCR solves 100 % of the frames unless noted; classical and the anchor network report the share their 50 mm jump gate accepted.

Fit on the room scans (v1, last epoch): coordinates 4.0–6.9 mm, pose of the training frames 1.2–1.7 mm / 0.09–0.15° (3XX 6.9 / 1.6; A 6.6 / 1.7; B 4.0 / 1.2; C 5.1 / 1.5). The 4XX models fit their room scans *better* than the 3XX model — the 4XX gap is not a fitting problem.

### 3.3 Outdated room scans (map of one session, sweeps of a later one)

| map → sweeps | SCR + Kabsch | SCR + PnP | classical anchors | RPR anchor network | first SCR |
|---|---|---|---|---|---|
| 2XX → 3XX (same room, small objects moved) | **6.5 / 11.8, 0.44°** | 21.2 / 47.8 | 10.4 / 20.3 | 39.8 / 71.1 (82 %) | — |
| A → B (small rearrangement) | 14.0 / 25.4, 0.56° | 31.7 / 47.3 | **7.9 / 12.9** (92 %) | 81.6 / 103.9 (50 %) | 50.3 |
| A → C (large rearrangement) | **13.4** / 113.0, 1.30° (100 % solved) | 47.4 / 65.2 | 80.1 / 98.3 (21 %) | 51.8 / 108.8 (64 %) | 55.3 |

PnP is fooled by the changed appearance; a 3D–3D fit on measured geometry much less. A → C has a heavy tail that the inlier gate removes (section 3.6).

### 3.4 Room-scan coverage (`runs/coverage_error.md`, SCR v1 + PnP)

| split | frames covered (≤ 30 mm and 10° from a room-scan pose) | error covered | error not covered |
|---|---|---|---|
| 3XX | 96 % | 2.3 / 5.2 | 5.7 / 14.6 |
| 2XX val | 75 % | 4.9 / 9.6 | 8.1 / 16.7 |
| 4XX A | 5 % | 4.6 / 7.9 | 9.1 / 17.9 |
| 4XX B | 12 % | 5.6 / 12.1 | 9.1 / 18.0 |
| 4XX C | 0 % | – | 11.0 / 17.0 |
| 4XX D | 0 % | – | 14.4 / 29.2 |
| 4XX E | 14 % | 7.2 / 10.9 | 10.8 / 20.5 |
| 2XX → 3XX (outdated) | 19 % | 11.6 / 17.7 | 25.3 / 48.8 |
| **all pooled** | 17 % | **4.1** / 13.3 | **13.4** / 45.7 |

Within 4XX A the error grows with the distance to the nearest room-scan pose: 8.1 (< 30 mm), 8.5 (30–60 mm), 13.9 mm (60–100 mm).

### 3.5 Viewpoint augmentation (ACE: zoom 0.67–1.5, in-plane rotation ±15°)

| model | 2XX val, PnP | 2XX val, Kabsch | 4XX A, PnP | 4XX A, Kabsch | fit: pose of training frames (2XX) |
|---|---|---|---|---|---|
| v1 | 5.1 / 11.3 | **3.4 / 8.7** | 9.9 / 17.6 | 5.9 / 10.1 | 2.7 mm |
| v1 + augmentation | 6.6 / 13.5 | 6.5 / 10.1 | 6.1 / 10.8 | **5.1 / 8.1** | 6.3 mm |

Low-coverage validation split (2XX mapped on room-202 only, 0 % covered):

| model | PnP | Kabsch |
|---|---|---|
| v1 | 40.2 / 77.5 | **16.2 / 34.7** |
| v1 + augmentation | 23.2 / 53.9 | 18.2 / 36.4 |

Not adopted: with Kabsch the gain on 4XX A is within noise and the cost on both validation splits is 2–3 mm. The looser fit suggests the 0.17 M-parameter head lacks the capacity. The room-202-only split is a weak stand-in for 4XX (errors 3× larger, not tracking the pose distance).

### 3.6 Inlier gate for Kabsch anchors (≥ 400 inliers)

| split | all frames (median / p90) | gated | frames kept |
|---|---|---|---|
| 2XX val, 3XX, 4XX A, B, C | unchanged | unchanged | 99–100 % |
| 4XX D | 8.7 / 18.9 | 8.6 / 17.1 | 96 % |
| 4XX E | 6.5 / 13.9 | 6.2 / 11.5 | 94 % |
| A → C | 13.4 / 113.0 | **8.2 / 16.6** | 49 % |

(Pooled medians over frames.)

### 3.7 Full system: error at the US image (median per sweep, mean over sweeps; mean step-to-step error in brackets)

v1 model, each segment started at the true pose; superseded by 3.14 and 3.16 (the `sys-kabsch-*` files of this table were removed on 27 Oct and are in git commit 1648fcf, except the extended-map runs of 3.11).

Same pipeline, classical odometry, frames and settings for every column (pose graph: anchor σ 11 mm / 1°).

| split | classical odometry only | + classical anchors | + first SCR anchors | **+ SCR v1 + Kabsch** | + SCR v1 + Kabsch, no pose graph | + classical anchors, no pose graph |
|---|---|---|---|---|---|---|
| 2XX val | 36.9 (2.25) | **4.2** (2.28) | — | 4.4 (2.23) | 4.6 (2.39) | 5.0 |
| 3XX | 9.5 (1.18) | 3.2 (1.09) | 6.6 (1.23) | 2.6 (1.07) | **2.1** (1.15) | 2.9 |
| 4XX A | 15.2 (1.11) | **4.2** (1.13) | 16.3 (1.34) | 5.5 (1.11) | 5.8 (1.33) | 5.1 |
| 4XX B | 11.3 (1.41) | **3.4** (1.33) | 11.5 (1.61) | 5.7 (1.34) | 6.2 (1.50) | 3.1 |
| 4XX C | 8.9 (1.27) | **4.6** (1.19) | 14.5 (1.49) | 6.4 (1.18) | 6.5 (1.27) | 5.5 |
| 4XX D | 12.7 (1.32) | **6.3** (1.19) | 20.8 (1.52) | 10.2 (1.22) | 10.3 (1.43) | 7.0 |
| 4XX E | 13.0 (1.76) | **4.8** (1.57) | 14.5 (1.91) | 6.4 (1.65) | 6.2 (1.78) | 4.9 |

Pose-graph setting for SCR anchors (2XX validation): anchor σ 11 mm / 1° → 4.4, 5 mm / 0.5° → 4.4, 3 mm / 0.3° → 4.5 mm; no effect, default kept.

The camera-position anchor error does not carry over one to one: on 4XX C the SCR anchors are better at the camera (5.2 vs 5.9 mm) but worse at the US image (6.4 vs 4.6 mm) because their rotation is worse (0.74 vs 0.39°).

### 3.8 3D pages: mean pixel error over the compounded US images (`runs/volume3d-final/<split>/`)

Final configuration as in 3.16 (v2 model, gate recovery, every segment started from an anchor, pose graph; classical anchors with the same settings), every sweep. Mean pixel error (mm) per sweep, mean over the split's sweeps in bold.

| split | sweeps | **SCR + classical odometry** | classical + classical | classical odometry only | per sweep (SCR / classical) |
|---|---|---|---|---|---|
| 3XX | 5 | **2.7** | 3.2 | 10.1 | 313 2.5/3.8, 314 2.8/3.1, 315 2.3/2.9, 316 2.2/2.6, 317 3.7/3.8 |
| 4XX A | 8 | 5.3 | **4.4** | 14.5 | 401 4.1/3.1, 402 5.7/3.6, 403 4.9/3.8, 404 10.1/5.6, 405 5.9/4.0, 406 3.4/5.6, 407 4.2/3.7, 408 4.0/5.7 |
| 4XX B | 4 | 6.0 | **3.7** | 11.1 | 409 6.8/2.5, 410 5.8/3.8, 411 3.9/3.9, 412 7.5/4.5 |
| 4XX C | 4 | 6.9 | **5.3** | 9.8 | 413 4.2/4.7, 414 9.8/4.6, 415 5.5/5.1, 416 8.1/6.8 |
| 4XX D | 6 | 10.5 | **7.2** | 13.1 | 418 8.6/5.1, 419 9.8/7.0, 420 13.0/6.9, 421 10.9/7.3, 423 11.7/9.9, 424 8.9/6.7 |
| 4XX E | 4 | 7.8 | **5.2** | 13.8 | 425 6.1/5.1, 426 6.7/3.6, 427 13.7/8.2, 428 4.6/4.1 |

SCR is better on all five 3XX sweeps and on 3 of the 26 4XX sweeps (406, 408, 413; equal on 411). The pages of the earlier v1 / true-start runs (`volume3d-3XX`, `volume3d-4XX`, one sweep per 4XX block; 3XX 2.8 vs 3.3 mm) were removed on 27 Oct (git commit 1648fcf).

For reference (rgbd-us, same metric): classical odometry + first SCR 6.5 mm on 3XX, 12.0–21.4 mm on 4XX (run-426: 11.6 mm); classical odometry + adapted anchor network 5.7 mm on 3XX, 26.4–54.4 mm on 4XX.

### 3.9 US images (`tools/us_inplane.py`, `runs/us-*`)

Pairs of US frames k new frames apart; truth from Polaris through the US calibration.

**U1: in-plane rigid registration (ECC)**, mean point error over the US fan, median (mm):

| collection | k = 1: US / no motion | k = 3: US / no motion | k = 10: US / no motion | k = 10 out-of-plane motion |
|---|---|---|---|---|
| 2XX | 0.20 / 0.16 | 0.60 / 0.49 | 1.91 / 1.55 | 3.76 |
| 3XX | 0.19 / 0.18 | 0.57 / 0.58 | 1.80 / 1.80 | 4.48 |
| 4XX A | 0.18 / 0.15 | 0.53 / 0.45 | 1.63 / 1.47 | 2.96 |
| 4XX D | 0.17 / 0.12 | 0.48 / 0.34 | 1.52 / 1.07 | 2.85 |

The registration is no better than assuming no in-plane motion: the probe moves mostly out of plane and the cross-section changes rather than shifts. Dropped.

**U2: speckle decorrelation** — correlation after in-plane alignment vs the true out-of-plane distance (median ncc):

| out-of-plane | 2XX | 3XX | 4XX A | 4XX D |
|---|---|---|---|---|
| < 0.5 mm | 0.995 | 0.994 | 0.996 | 0.996 |
| 1–2 mm | 0.980 | 0.982 | 0.981 | 0.980 |
| 2–4 mm | 0.967 | 0.967 | 0.967 | 0.966 |
| 4–8 mm | 0.943 | 0.947 | 0.951 | 0.943 |
| > 8 mm | 0.911 | 0.918 | 0.921 | 0.918 |
| Spearman ρ | −0.83 | −0.85 | −0.83 | −0.83 |

Out-of-plane distance predicted from a curve built on **2XX only**:

| test | error median / p90 | baseline (predict the median distance) | at k = 10 (true distance) |
|---|---|---|---|
| 3XX | 0.43 / 2.61 mm | 0.77 / 5.33 | 1.29 (4.48) |
| 4XX A (new session) | 0.28 / 2.25 | 0.77 / 3.90 | 0.86 (2.96) |
| 4XX D (second subject) | 0.27 / 1.76 | 0.72 / 3.44 | 0.86 (2.85) |

The curve is the same in every collection and for both subjects, and transfers across sessions. It gives the distance only (the sign must come from the camera). Not yet tested inside the pose graph.

**U3: per-patch speckle against the system (27 Oct, first check on run-316 only, classical system; `tools/shape_error.py`, `tools/us_speckle.py`).** The camera system already gets the motion between nearby US frames right: out-of-plane error of the relative pose at the 5 US-image points, median 0.07 mm at 1 row, 0.28 mm at 8 rows, 0.58 mm at 30 rows (1 s), against a true motion of 0.5, 4.1 and 15 mm. Per-patch speckle (12 mm patches, plane fit = elevational shift + two tilts) is 5–10× worse, even with the sign from Polaris and an in-sample curve: 0.33 / 0.75 / 2.4 mm at 1 / 4 / 8 rows; replacing the system where US disagrees by more than 1–3 mm makes the mean and p99 worse, not better. The error that is left is long-range: after the best rigid fit of the whole sweep it is still 2.1 of 2.3 mm (it is distortion, not an offset), and speckle cannot measure beyond a few mm. Running on every split (2XX decides) is pending; if confirmed, short-range US factors are dropped and only long-range constraints (crossing planes) remain.

### 3.10 Further experiments (23 Oct)

**E1: refining the final pose fit** (same models, Kabsch inliers refitted; rule fixed in advance: adopt if the 2XX rotation improves without a worse position error).

| split | plain Kabsch (v1) | weighted by depth noise | joint reprojection + depth |
|---|---|---|---|
| 2XX val (decides) | **3.4 / 8.7, 0.33°** | 4.7 / 9.5, 0.37° | 3.6 / 9.5, 0.34° |
| 3XX | **2.0 / 3.3**, 0.19° | 2.1 / 4.6, 0.21° | 2.0 / 3.9, 0.18° |
| 4XX A | **5.9 / 10.1, 0.48°** | 7.2 / 12.0, 0.54° | 7.3 / 11.3, 0.51° |
| 4XX B | 5.9 / 9.2, 0.40° | 7.6 / 13.7, 0.58° | **5.3** / 10.3, **0.37°** |
| 4XX C | **5.2 / 10.1, 0.74°** | 6.6 / 14.0, 0.94° | 5.7 / 13.2, 0.80° |
| 4XX D | **9.3 / 18.9, 0.73°** | 10.5 / 21.4, 0.82° | 11.8 / 21.7, 0.84° |
| 4XX E | **5.9 / 13.9, 0.46°** | 6.2 / 16.8, 0.62° | 7.3 / 15.5, 0.58° |

Not adopted. Down-weighting far cells removes the long lever arms that constrain rotation; adding reprojection does not help either. The rotation error comes from the predicted coordinates, not from the solver.

**T1 / T3: bigger head and cleaner labels** (2XX validation, 120 epochs; rule: adopt if > 1 mm better).

| model | PnP | **Kabsch** | rotation (Kabsch) | fit: pose of training frames | s / epoch |
|---|---|---|---|---|---|
| v1 (small head, 0.17 M) | 5.1 / 11.3 | 3.4 / 8.7 | 0.33° (p90 0.58) | 2.7 mm / 0.16° | 26 |
| big head (2.18 M) | 4.6 / 9.6 | 3.4 / 8.0 | 0.29° (p90 0.53) | 2.3 / 0.12 | 25 |
| clean labels (< 2 m, no depth edges) | 6.1 / 10.3 | 3.5 / 8.0 | 0.31° (p90 0.61) | 2.3 / 0.13 | 35 |
| big head + clean labels | 5.0 / 10.9 | 3.4 / **7.3** | **0.27°** (p90 0.50) | 2.1 / 0.11 | 34 |

The median does not move (rule not met), but the p90 (8.7 → 7.3 mm) and the rotation (0.33 → 0.27°) improve, most with both changes; whether this exceeds seed noise is unknown (the seed repeat measured the median only). The big head costs no time. (The clean-label models' fit check shows ~100 mm after the rigid fit because they have no labels beyond 2 m and the fit check scores cells up to 3 m; Kabsch leaves those cells out.)

**T4: more mapping data** (labelled extra; 4XX A mapped on its room scans **plus sweeps run-401…404**, 9,813 frames, tested on run-405…408; the extra sweeps are labelled with Polaris poses).

| map | PnP | **Kabsch** | rotation (Kabsch) | per sweep (Kabsch): 405 / 406 / 407 / 408 |
|---|---|---|---|---|
| room scans only (v1) | 9.5 | 5.3 | 0.47° | 7.1 / 2.9 / 5.0 / 6.0 |
| room scans + 4 earlier sweeps | 2.4 / 7.4 | **1.9 / 5.5** | **0.22°** | 1.7 / 1.1 / 2.2 / 2.4 |
| classical anchors, room scans only (whole block A) | | 5.3 / 10.1 | 0.48° | |

With views close to the test viewpoints in the map, 4XX A behaves like 3XX: 1.9 mm and 0.22°, a third of the error, and the rotation problem disappears. Coverage, not the model, limits 4XX. Caveats: same subject and session, so the earlier sweeps view the room from nearly the same places; Polaris labels (in use these would be the system's own estimated poses); classical anchors were not given the extra keyframes.

**E3: SCR only, no classical odometry** (SCR anchor every 0.25 s; median error at the US image, step-to-step error in brackets).

| split | SCR + classical odometry (pose graph / offline) | **SCR only, offline** | SCR only, pose graph |
|---|---|---|---|
| 2XX val | 4.4 (2.23) / 4.6 (2.39) | **3.8** (2.87) | 6.4 (1.94) |
| 3XX | 2.6 (1.07) / 2.1 (1.15) | 2.1 (1.69) | 4.6 (1.61) |
| 4XX A | 5.5 (1.11) / 5.8 (1.33) | 5.9 (1.85) | 7.6 (1.44) |

Without odometry the median accuracy is the same (2XX even better, where the classical odometry drifts 64 mm on run-205), but the trajectory is 1.4–1.7× jumpier from step to step. The pose graph with zero odometry has no motion model and smooths wrongly (worse median). Classical odometry is needed only for smoothness; a constant-velocity motion model or a learned matcher could replace it.

### 3.11 Extended maps: coverage curve, second block, fair comparison, full system (23 Oct)

Maps extended with earlier sweeps of the same block (labelled with Polaris poses, as the room scans); tested on the later sweeps only. All numbers on the same test sweeps.

**Coverage curve, 4XX A** (test run-405…408; SCR anchors, Kabsch; mean of per-sweep medians / p90, rotation):

| map | frames | anchor error | rotation |
|---|---|---|---|
| room scans only (v1) | 3,893 | 5.3 | 0.47° |
| + 1 sweep (run-401) | 5,679 | 2.4 / 6.6 | 0.27° |
| + 2 sweeps (run-401, 402) | 6,851 | **1.9 / 5.4** | 0.23° |
| + 4 sweeps (run-401…404) | 9,813 | 1.9 / 5.5 | 0.22° |
| + 4 sweeps, big head + clean labels | 9,813 | 1.8 / 5.2 | 0.22° |

One extra sweep gives most of the gain; two saturate it. Big head + clean labels add nothing measurable here.

**Fair comparison and full system** (classical anchors given the same extra keyframes; median error at the US image with the pose graph, without it in brackets):

| block, test sweeps | map | SCR anchors | classical anchors | **SCR system** | classical system |
|---|---|---|---|---|---|
| A, run-405…408 | room scans only | 5.6, 0.47° | 5.9, 0.48° | 5.0 (5.4) | **4.5** (5.6) |
| A, run-405…408 | + run-401…404 | **2.0 / 4.6, 0.20°** | 3.7 / 7.0, 0.36° | **2.3 (2.1)** | 3.2 (3.5) |
| D, run-421, 423, 424 | C's room scans only | 8.6, 0.76° | 7.4, 0.46° | 10.2 | **7.2** |
| D, run-421, 423, 424 | + run-418…420 | **3.3 / 7.7, 0.27°** | 4.7 / 14.6, 0.35° | **4.5 (3.7)** | 5.8 (5.0) |

Both methods gain from the extra keyframes, SCR far more: at the US image SCR goes 5.0 → 2.3 mm (A) and 10.2 → 4.5 mm (D), classical 4.5 → 3.2 and 7.2 → 5.8 mm. With extended maps SCR is the better system on both blocks, including the second subject; with room scans only, classical is better. SCR's rotation drops below classical's (0.20–0.27 vs 0.35–0.36°). The pose graph (anchor σ 11 mm / 1°, set for weaker anchors) now costs SCR accuracy (D: 4.5 vs 3.7 mm without it).

Caveats: the extra sweeps are labelled with Polaris poses (in use: the system's own estimated poses), they come from the same subject and session as the test sweeps, and two blocks were tested.

### 3.12 Map extension without Polaris: earlier sweeps labelled with the system's own poses (23 Oct)

The extra sweeps are localised by the full system with the room-scan-only model (SCR + Kabsch anchors, classical odometry, pose graph, each segment **started from an SCR anchor**, no Polaris pose anywhere), exported with `poses.py`, and used as training labels (`scr_anchor.py train --label-poses`). Test on the later sweeps (Kabsch).

| block, test sweeps | room scans only | + sweeps, **estimated poses** | + sweeps, Polaris poses | error of the estimated labels vs Polaris (median / p90) |
|---|---|---|---|---|
| A, run-405…408 (+ run-401, 402) | 5.3, 0.47° | **5.0 / 8.4, 0.48°** | 1.9 / 5.4, 0.23° | 4.6 / 8.0 and 5.8 / 7.4 mm, 0.39–0.52° |
| D, run-421, 423, 424 (+ run-418…420) | 9.0, 0.76° | **7.9 / 11.2, 0.60°** | 3.1 / 7.0, 0.22° | 7.4 / 17.8, 7.6 / 18.1, 13.7 / 21.9 mm, 0.65–0.95° |

Self-labelling recovers almost none of the gain (A 5.3 → 5.0, within noise; D 9.0 → 7.9). The network learns the extra views *with the errors of the poses that labelled them*, so the later sweeps are localised about as well as those labels (5–8 mm), not better: map extension is only as good as the poses of the added views. Making it work needs labels more accurate than the anchors themselves — e.g. refining the new sweep's poses against the room scan geometry before training (as ACE0 refines poses during mapping), or adding only frames whose anchors are confidently correct — otherwise the practical route to coverage is a better room scan.

### 3.13 Seed repeats, big head + clean labels decided, inlier gate (24 Oct)

**Seed repeats of the final model** (SCR anchors, Kabsch, per-second evaluation; mean of per-sweep medians / p90, rotation):

| split | seed 0 | seed 1 | seed 2 | classical anchors |
|---|---|---|---|---|
| 3XX | 2.0 / 3.3, 0.19° | 1.9 / 3.6, 0.18° | 2.2 / 3.8, 0.19° | 2.6 / 6.9, 0.34° |
| 4XX A | 5.9 / 10.1, 0.48° | 5.8 / 10.1, 0.49° | | 5.3 / 10.1, 0.48° |

On 3XX the spread over three seeds is 0.3 mm (1.9–2.2 mm), and every seed is below classical in median (0.4–0.7 mm), p90 (3.3–3.8 vs 6.9 mm) and rotation (0.18–0.19 vs 0.34°). The run-to-run noise on 3XX (140 frames) is much smaller than the ~1 mm measured on 2XX validation (77 frames, 2 sweeps): the 3XX anchor advantage is robust. 4XX A is equally stable (5.9 / 5.8 mm). The system-level 3XX result (2.8 vs 3.3 mm mean pixel error) was measured for seed 0 only.

**Big head + clean labels, second seed** (2XX validation, Kabsch; rule fixed in advance: adopt if rotation and p90 are lower than the small head for both seeds):

| seed | small head (v1) | big head + clean labels |
|---|---|---|
| 0 | 3.4 / 8.7, 0.33° | 3.4 / **7.3**, **0.27°** |
| 1 | 3.5 / 9.4, 0.37° | 3.7 / **6.9**, **0.28°** |

Rule met for both seeds: p90 −1.4 and −2.5 mm, rotation −0.06 and −0.09°, median unchanged within noise. **Adopted** (`--head big --label-max-depth 2000 --drop-depth-edges`). Its effect on the test splits, where rotation limits the error at the US image, is not measured yet; on the extended map (4XX A + 4 sweeps) it changed nothing (1.8 vs 1.9 mm).

**Inlier gate** (full system, 4XX D and E, the splits where the ≥ 400-inlier gate removed anchors):

| split | gated: anchors (median / p90), US image | ungated: anchors, US image |
|---|---|---|
| 4XX D | 9.0 / 16.7 mm, **10.2** mm | 9.4 / 18.7 mm, **10.1** mm |
| 4XX E | 5.9 / 12.0 mm, **6.4** mm | 6.1 / 15.9 mm, **6.5** mm |

The gate trims the anchor p90 but does not change the error at the US image (the pose graph already absorbs the outliers). The concern that it was chosen after seeing the test splits therefore does not affect the system results; report the ungated numbers or say this.

### 3.14 Strict protocol for 3XX, final system without a ground-truth start, big head + clean labels on the test splits (24 Oct)

**3XX with the room scan recorded before the sweeps.** The 3XX room scans were recorded during (room-301, between run-314 and run-315) and after (room-302) the sweeps. Strict check: map on room-301 only (52 s, 1,569 frames), test on the sweeps recorded after it (run-315…317).

| run-315…317 | SCR anchors (Kabsch, per second) | classical anchors (full system, anchor times) | classical, US image |
|---|---|---|---|
| map room-301 + room-302 | **1.8** (2.1 / 1.3 / 2.1), 0.20° | 2.5 (2.5 / 1.9 / 3.0), 0.29° | 2.9 |
| map room-301 only (strict) | 3.1 / 6.1 (4.0 / 2.3 / 3.1), **0.26°** | **2.7 / 6.1** (3.5 / 1.8 / 2.7), 0.32° | 3.0 |

Under the strict protocol SCR is on par with classical anchors on 3XX (median 3.1 vs 2.7 mm, same p90, better rotation), not better. SCR loses more from the shorter map (1.8 → 3.1 mm) than classical (2.5 → 2.7 mm): the coverage dependence of section 3.4 again. The 3XX advantage of sections 3.2–3.8 depended partly on room-302, recorded after the sweeps. The SCR full-system run for this check (`sys-kabsch-3XX-room301`) is still to be run.

**Final system, every segment started from an anchor (no Polaris pose at test time)**; median error at the US image (mm), offline pose graph, step-to-step error in brackets; without the pose graph in square brackets.

| split | **SCR + classical odometry** | classical + classical | ratio |
|---|---|---|---|
| 2XX val | 4.3 (2.22) [4.6] | 4.2 (2.27) [5.1] | 1.0 |
| 3XX | **2.6** (1.08) [**2.2**] | 3.1 (1.09) [2.9] | 0.8 |
| 3XX, seeds 1 / 2 | 2.7 / 2.7 [2.2 / 2.2] | | |
| 4XX A | 5.5 (1.10) | **4.2** (1.13) | 1.3 |
| 4XX B | 6.0 (1.34) | **3.4** (1.32) | 1.8 |
| 4XX C | 6.7 (1.17) | **4.9** (1.19) | 1.4 |
| 4XX D | 10.3 (1.21) | **6.3** (1.19) | 1.6 |
| 4XX E | 6.6 (1.64) | **5.0** (1.57) | 1.3 |

Starting from an anchor instead of the true pose changes nothing (3XX 2.6, A 5.5 as before). The 3XX system result is stable over three seeds (2.6–2.7 mm). On 4XX classical is 1.3–1.8× better at the US image.

**Big head + clean labels on the test splits** (anchors, Kabsch; v1 → v2):

| split | v1 (small head) | v2 (big head + clean labels) | classical anchors |
|---|---|---|---|
| 3XX | 2.0 / 3.3, 0.19° | 1.8 / 3.4, 0.19° | 2.6 / 6.9, 0.34° |
| 4XX A | 5.9 / 10.1, 0.48° | 5.4 / 8.9, 0.45° | 5.3 / 10.1, 0.48° |
| 4XX B | 5.9 / 9.2, 0.40° | 5.6 / 8.0, 0.35° | 3.2 / 5.0, 0.25° |
| 4XX C | 5.2 / 10.1, 0.74° | **4.8 / 9.9, 0.59°** | 5.9 / 11.1, 0.39° |
| 4XX D | 9.3 / 18.9, 0.73° | 8.6 / 14.5, 0.64° | 7.1 / 18.3, 0.41° |
| 4XX E | 5.9 / 13.9, 0.46° | 5.7 / 9.7, 0.40° | 5.2 / 8.5, 0.35° |

v2 improves every split, most in p90 (D 18.9 → 14.5, E 13.9 → 9.7 mm) and rotation (−0.04 to −0.15°), confirming the 2XX decision. The gain is too small to close the 4XX gap: classical anchors stay better on B, D, E and in rotation everywhere. Full-system runs with v2 are still to be run.

### 3.15 Multi-frame anchors and gate recovery (2XX validation, 24 Oct)

Full system, v2 model (big head + clean labels), every segment started from an anchor, gate recovery after 3 agreeing rejected anchors; `--scr-frames M` pools the correspondences of M chain frames (0.27 s apart) linked by the odometry. Median error at the US image (offline pose graph), step-to-step error in brackets; anchors median / p90, rotation.

| anchors from | anchors | US image |
|---|---|---|
| 1 frame (M = 1) | 3.6 / 6.3, 0.29° | **4.2** (2.22) |
| 3 frames | 3.6 / 7.0, 0.29° | 4.4 (2.22) |
| 5 frames | 3.8 / 7.4, 0.28° | 4.5 (2.24) |
| v1, 1 frame, no recovery (reference) | 3.5 / 8.4, 0.33° | 4.3 (2.22) |
| classical anchors (reference) | 5.2 / 11.9, 0.33° | 4.2 (2.27) |

Multi-frame anchors are not adopted (rule fixed in advance: > 0.2 mm better than one frame; they are 0.2–0.3 mm worse). Pooling triples the inliers but the odometry linking the frames adds its own error, and the rotation barely changes (0.29 → 0.28°): the rotation error of single-frame anchors is not mainly noise that more correspondences average out. Gate recovery never triggered on 2XX (no wrongly accepted anchor), so it changes nothing there; it is kept for the 4XX failure (run-404).

### 3.16 Final system on the test splits (27 Oct)

Both anchor types with gate recovery (3), every segment started from an anchor (no Polaris pose at test time), classical odometry, pose graph. SCR: v2 model (big head + clean labels), one frame per anchor. Median error at the US image (mm), step-to-step error in brackets; anchors median / p90, rotation.

| split | SCR anchors | classical anchors | **SCR system** | **classical system** | ratio |
|---|---|---|---|---|---|
| 3XX | 1.9 / 3.3, 0.19° | 2.6 / 6.9, 0.34° | **2.6** (1.08) | 3.1 (1.09) | 0.8 |
| 4XX A | 5.5 / 8.2, 0.48° | 5.3 / 10.0, 0.48° | 5.0 (1.10) | **4.2** (1.13) | 1.2 |
| 4XX B | 5.8 / 7.8, 0.35° | 3.2 / 5.0, 0.25° | 5.7 (1.33) | **3.4** (1.32) | 1.7 |
| 4XX C | 4.9 / 10.5, 0.64° | 6.0 / 11.1, 0.39° | 5.9 (1.17) | **4.9** (1.19) | 1.2 |
| 4XX D | 8.3 / 12.8, 0.65° | 7.1 / 16.6, 0.41° | 9.6 (1.18) | **6.3** (1.19) | 1.5 |
| 4XX E | 5.3 / 9.3, 0.40° | 5.2 / 8.4, 0.36° | 6.5 (1.65) | **5.0** (1.57) | 1.3 |

Gate recovery fixed the v2 failure on run-404 (US image 28.3 → 8.2 mm, anchors accepted 38 → 95 %) and changed nothing for classical anchors (identical results). Against v1 (3.14), v2 lowers the 4XX system error by up to 0.8 mm; the gap to classical is now 1.2–1.7× on 4XX.

## 4. Why SCR beats the RPR anchor network

| | RPR anchor network | SCR |
|---|---|---|
| network output | **one** 6-DoF relative pose (keyframe → frame) per image pair | **~3,600** room coordinates per image, one per cell |
| who computes the pose | the network's last layer | geometry: RANSAC + Kabsch on the measured depth |
| what it must learn | a general rule "image pair → motion" valid in any session | one fact about one room: "this patch is at (x, y, z)" |
| training data | (keyframe, frame) RGB-D pairs from earlier sessions (2XX + 3XX), adapted 5 epochs on the new room scan | the room scan of the session it is used in (120 epochs) |
| wrong image content (moved objects, hands) | mixed into the single pose; it cannot reject them (rgbd-us saliency and masking test) | those cells become RANSAC outliers and are dropped |
| needs a keyframe near the current pose | yes; its error grows with keyframe distance (3XX 5.6 / 7.5 / 10.6 mm at 0–20 / 20–40 / 40–60 mm; 78 % of 4XX anchors > 60 mm away) | no |
| anchor error | 15 mm (3XX), 25–67 mm (4XX), 37–93 % accepted | 2.0 mm (3XX), 5–9 mm (4XX), 100 % solved |

1. **Outlier rejection.** One wrong region spoils a regressed pose; SCR loses only those cells (on 3XX ~2,600 of 3,600 cells are inliers, the rest are ignored). This is also why SCR + Kabsch survives the large room change (A → C, 13 mm) while the regression network does not (52 mm).
2. **Precision from averaging many correspondences, not from one regression.** Each predicted coordinate is 7–12 mm off; a rigid fit through thousands of them is ~2 mm (3XX). The probe moves only 2–5 mm per step, and a regression network has an error floor of about 1–2 mm and 0.1–0.2° even when it works, with nothing to average.
3. **No cross-session generalisation needed.** rgbd-us found that the regression networks learn the session, not the geometry (anchor network: 3.1 mm on training data, 8.1 mm on validation, 15–20 mm in a new session). SCR is retrained on each session's own room scan, so memorising the room is exactly its job. The generalisation it still needs — to new viewpoints in the same room — is exactly where it fails (4XX, section 3.4).
4. **Geometry is left to geometry.** Intrinsics, depth and the rigid transform are known exactly; SCR hands them to an exact solver, RPR has to approximate projective geometry inside a network.

Fairness: both used depth (the anchor network took RGB-D pairs); SCR received more per-session training (120 epochs vs 5 epochs of adaptation); neither generalises to unseen viewpoints. The structural difference — local predictions plus robust geometry against one regressed pose — is what the data supports: the anchor-error gap is 3–6× on every split, and the saliency test showed directly that the regression network cannot reject outliers.

## 5. Practical comparison with classical anchors (SIFT + PnP-RANSAC with depth)

| | classical anchors | SCR anchors |
|---|---|---|
| needs | room-scan keyframes, a pose prior to retrieve nearby keyframes (odometry, or a search over ~200 keyframes at the start) | a network trained on the room scan (20–50 min GPU), no prior, no keyframes |
| unchanged room, good coverage (3XX) | 2.6 mm anchors, 3.3 mm system | **2.0 mm anchors, 2.8 mm system** |
| new session, short room scans (4XX) | **3.2–7.1 mm anchors, 3.6–7.0 mm system** | 5.2–9.3 mm anchors, 4.9–10.1 mm system |
| rotation | **0.25–0.48°** | 0.19° (3XX), 0.40–0.74° (4XX) |
| large room change (A → C) | breaks (80 mm, 21 % accepted) | **13 mm median**, heavy tail without the gate |
| speed per anchor | not measured | 50–75 ms (Kabsch, numpy), 10 ms (PnP) |

## 6. Critical points and limitations

**Evaluation**
1. **Small test sets.** 3XX is 5 sweeps / 140 anchor frames; the 3D pages cover 5 + 5 sweeps (one per 4XX block). The 3XX win (2.8 vs 3.3 mm) is consistent (4 of 5 sweeps better or equal) but about half the measured run-to-run noise: "at least as good as classical", not "clearly better".
2. **The gate threshold (400 inliers) was chosen after looking at the inlier distributions of all splits**, including the test splits (on 2XX validation every frame passes, so it could not be chosen there). It does not change the unchanged-room results but does affect D, E and the outdated-map numbers. Fix it in advance for new data, or report ungated numbers alongside.
3. **Anchor-level comparison with classical is close but not identical:** classical is evaluated at the odometry chain's anchor times with a pose prior (keyframes retrieved near the odometry pose); SCR every 30 rows without a prior. The full-system comparisons (3.7, 3.8) are fully matched.
4. **Both methods map the room with Polaris poses.** In deployment the room-scan poses would come from SLAM or ACE0-style reconstruction; both would degrade, by an unknown amount.
5. **One seed per setting** except the 60-epoch repeat; one model per session.
6. The hand-eye calibration (3.5 mm board-corner error) enters both the labels and the ground truth; view-dependent label errors are a floor for SCR that classical largely cancels by chaining off a nearby keyframe.

**Method**
1. **Coverage is the main limit:** SCR memorises the room from the room-scan viewpoints and does not extrapolate; better room scans help both methods, SCR more.
2. **Rotation is SCR's weak spot on 4XX**, and the US image is 16 cm from the camera, so it dominates the error there.
3. **Cost:** per-session GPU training; Kabsch in numpy is 5–7× slower than PnP (easily moved to the GPU).
4. **Not yet tried:** a larger (ACE-sized) head, RGB-D input, a better rotation estimate, the reprojection loss, the US out-of-plane factor in the pose graph.

## 7. Next steps

| priority | step | expected effect |
|---|---|---|
| 1 | Better anchor rotation: weight cells by 1/z², or jointly refine reprojection + depth residuals on the Kabsch inliers | the largest gain at the US image on 4XX |
| 2 | Larger head (~4 M parameters, ACE-sized), then viewpoint augmentation again | generalisation to unseen viewpoints (4XX B, D) |
| 3 | US out-of-plane factor (U3): speckle-decorrelation distance between US frames as a partial factor in the pose graph | smoother and more accurate frame spacing at the US image |
| 4 | Room-scan protocol for new recordings: record until `check_coverage.py` reports most sweep viewpoints covered | coverage is the largest error source |
| 5 | For publication: room-scan poses without Polaris, more seeds, more sweeps, a gate fixed in advance | credibility of the comparison |

## 8. Files and how to reproduce

| file | purpose |
|---|---|
| `scr_anchor.py` | `train` (final recipe by default; `--head`, label cleaning, viewpoint augmentation, `--label-poses`) and `eval` (`--solver kabsch/pnp`); uses `scr.py`, `dataloader.py`, `geometry.py` in the repo root (copies of rgbd-us), runs without rgbd-us |
| `tools/anchoring_kabsch.py` | rgbd-us `anchoring.py` (full system) with SCR + Kabsch anchors and the inlier gate |
| `tools/volume_pages.py` | interactive 3D pages from anchoring results (rgbd-us `poses.py` + `tools/volume_3d.py`) |
| `tools/coverage_error.py` | anchor error vs distance to the nearest room-scan pose |
| `tools/us_inplane.py` | US diagnostics U1 (in-plane registration) and U2 (speckle decorrelation) |
| `tools/draw_scr_anchor_diagram.py` | block diagram of the pipeline |
| `note.md` | working notes, data guide, full history |

| runs | content |
|---|---|
| `runs/s0a-scr-3XX` | evaluator check |
| `runs/s1-base-2XX`, `s1-2XX`, `s1-e60-2XX`, `s1-e60-seed1-2XX`, `s1-e120-2XX`, `s3-full-2XX` | training study on 2XX (3.1) |
| `runs/v1-3XX`, `v1-4XXA/B/C` | v1 on the test splits; `eval_*` (PnP) and `eval_*_kabsch` (3.2, 3.3) |
| `runs/aug-2XX`, `aug-4XXA` | viewpoint augmentation (3.5); the room-202-only validation runs were removed (numbers in 3.5, files in git commit 5f80808) |
| `runs/coverage_error.md` | coverage analysis (3.4) |
| `runs/README.md` | index of every run: purpose, data, settings, key result, status |
| `runs/sys-final-*`, `sys-v2r-*`, `sys-classical-r-*` | full system, error at the US image (3.14, 3.16) |
| `runs/volume3d-final/<split>/` | 3D pages, every sweep (3.8) |
| `runs/us-*` | US diagnostics (3.9) |

Commands to reproduce everything from this repo: `README.md`.
