# Markerless Probe Pose Estimation from a Probe-Mounted RGB-D Camera

## Summary (20 Oct 2026)

A probe-mounted RGB-D camera tracks the US probe without external markers: **odometry** between frames, corrected about once per second by **anchors** (absolute poses against a room scan recorded before the exam), combined in an offline pose graph.

**Main result: geometry beats the learned networks.** Classical odometry + classical anchors (SIFT + PnP-RANSAC with the RealSense depth, nothing trained) reach a mean error at the US image of **3.3 mm (Dice 0.95) on 3XX** and **3.6–7.0 mm on the 4XX blocks** (new session, room changes, second subject, occlusion), also when the sweep starts from the anchors instead of the Polaris pose. The learned system (RPRNet odometry + anchor network) reached 8.5 mm on 3XX only with session adaptation and failed on 4XX. A learned anchor with geometric outlier rejection (scene coordinate regression, SCR) is far better than the regression network but 3–5× worse than classical anchors. **US is not used in any final system** (§6.7).

**Fair comparison: every odometry × every kind of anchor** (mean pixel error at the US image after compounding, mm; 4XX: range over blocks A–E, except the network row, which is the median error from the anchoring tables; pose graph; anchors every 1 s; true start pose):

| odometry ↓ / anchors → | none | anchor network (regression) | SCR (learned, + PnP-RANSAC) | classical (SIFT + PnP-RANSAC) |
|---|---|---|---|---|
| RPRNet, 3XX | 38.6 | 13.9; 8.5 adapted | 8.8 | 6.2 |
| RPRNet, 4XX | 33.5–46.8 | failed: *30–58* (median), adapted | 12.5–29.6 | 5.4–8.0 |
| classical, 3XX | 10.1 | 11.4; 5.7 adapted | 6.5 | **3.3** |
| classical, 4XX | 9.9–14.5 | failed: 26.4–54.4, adapted | 12.0–21.4 | **3.6–7.0** |

**4XX per block** (mean pixel error, mm; * median from the anchoring tables, the export was removed):

| odometry + anchors | A, new session | B, small room change | C, large room change | D, subject 2 | E, occlusion |
|---|---|---|---|---|---|
| RPRNet only | 42.7 | 34.3 | 37.9 | 33.5 | 46.8 |
| RPRNet + anchor network (adapted)* | 43.6 | 30.0 | 41.3 | 57.8 | 48.3 |
| RPRNet + SCR | 16.7 | 12.5 | 19.5 | 22.2 | 29.6 |
| RPRNet + classical | 8.0 | 5.4 | 6.1 | 7.5 | 8.0 |
| classical only | 14.5 | 11.1 | 9.9 | 13.1 | 13.7 |
| classical + anchor network (adapted) | 36.9 | 26.4 | 47.5 | 54.4 | 51.4 |
| classical + SCR | 16.3 | 12.0 | 15.6 | 21.4 | 16.5 |
| **classical + classical** | **4.6** | **3.6** | **5.2** | **7.0** | **5.1** |

- **The anchors decide the result:** classical anchors give the best result with either odometry; the anchor network makes every 4XX block worse than no anchors, even with good odometry; SCR is in between and only helps the weak RPRNet odometry.
- **Better odometry still matters:** with classical anchors, classical odometry roughly halves the error against RPRNet (3XX 3.3 vs 6.2 mm, 4XX 3.6–7.0 vs 5.4–8.0 mm) and lets the anchors be sparse (§6.9).
- **Hardest block:** D (subject 2) for the best system (7.0 mm), E (occlusion) for the learned methods.

**Conclusions**
1. **Odometry alone is not enough, anchors alone are not either** (§6.9): without anchors the error grows with time (classical odometry: 9–15 mm median vs 3–6 mm with anchors every 1–2 s; RPRNet: 38 mm); anchors without odometry are about as accurate in the median but jump from step to step (step-to-step error 2–4× larger, 4× more anchor computations). Odometry gives smooth local motion and lets anchors be sparse (every 5 s costs 1–2 mm with classical odometry); anchors remove the drift.
2. **Anchoring needs outlier rejection and room-scan coverage.** Pose regression from a pooled image comparison cannot reject moved objects or hands (§6.4); RANSAC can. The room scan must cover the sweep viewpoints (§6.3).
3. **Classical is good enough here, with known limits** (§7): texture and a mostly unchanged room (a large room change breaks it: 80 mm anchors), the depth sensor's range and noise, not real-time as written, still above the 2 mm target.
4. **Direct pose regression generalises poorly** (RPRNet, anchor network, US-only networks, Li et al.): good within a training session, much worse in a new one (§6.1, §6.7), as the deep-VO literature reports (§6.8).

## 1. Problem and claim

Freehand 3D ultrasound needs the 6-DoF pose of every B-mode frame. Optical and EM trackers are accurate but expensive, line-of-sight constrained and tie the exam to a prepared room; US-only sensorless methods drift far beyond the ~2 mm budget set by the elevational beam width.

The approach: a single probe-mounted RGB-D camera looking at the room; nothing outside the probe at run time apart from a room scan recorded with the same camera before the exam. **The claim is "a useful pose without a prepared room", not better accuracy than a tracker** (optical ~0.5 mm, MLRecon 0.88 mm). Uses: 3D volume reconstruction and navigation relative to scanned anatomy.

**Positioning.** Closest neighbours: sensorless US (RecON, MoNet, DualTrack, Li et al.; ~5 % normalised drift) and probe-mounted VIO (He 2024: 3.78 mm / 0.36°; Buchanan 2024). The competitor to answer is MLRecon 2026 (external tripod RGB-D camera + probe CAD render-and-compare, 0.88 mm / 0.48°): it needs an unobstructed external camera, we need nothing outside the probe. Zhang 2025 needs a prepared textured workspace, Dai 2024 fiducials in a gel pad.

## 2. Method

```
T_world_cam = T_world_marker · T_marker_cam      (Polaris + hand-eye; ground truth and training labels only)
step:   T_k_k1 = inv(T_world_cam_k) · T_world_cam_k1           anchor:  T_world_cam = T_world_key · T_key_cam
```

**Pipeline** (`anchoring.py evaluate`):
1. **Odometry** on every step (frame gap 8, ~267 ms, 2–5 mm), chained from the start pose.
2. **Anchor** every 1 s: the 3 room-scan keyframes nearest the current odometry pose are retrieved (no ground truth), each gives an absolute pose, the poses are averaged; accepted unless it jumps > 50 mm from the current estimate.
3. **Combine:** offline pose graph (odometry steps + accepted anchors; anchor sigma 11 mm / 1°, confirmed on 2XX validation, §6.5), or reset the pose at each anchor for live use.
4. **Start pose** (`--start anchor`): from the anchors with no prior (classical: the best of 200 keyframes across the map; SCR: directly). Costs nothing measurable (§6.5).

**Classical solver** (`tools/anchor_classical.py: pnp_pose`), used for odometry (frame k → k+8) and anchors (keyframe → frame): SIFT on full-resolution RGB (≤ 4000 features), ratio test 0.8, frame-A keypoints lifted to 3D with A's depth, PnP + RANSAC (4 px, ≥ 20 inliers), refined on the inliers. RANSAC drops mismatches and moved objects. Settings fixed before any test.

**SCR anchors** (`scr.py`, diagram `tools/scr_diagram.pdf`): EfficientNet-B0 (stride-8 and stride-16 features fused) + a 1×1-conv head predicting the 3D room coordinate of each cell of a 45 × 80 grid; trained per room scan (targets: room-scan depth back-projected with the room-scan poses, Huber loss, 15 epochs); pose by PnP-RANSAC (10 px, ≥ 30 inliers) on the 3600 2D–3D pairs; no retrieval or prior pose needed.

**Learned system (superseded, diagram `tools/model_diagram.pdf`):** RPRNet regresses the relative pose `xi = se3_log(T_k_k1)` from an image window: EfficientNet-B0 stages 1–4 → correlation between frames → bidirectional GRU over 8-frame windows → pose head (odometry: RGB, `runs/rpr-rgb-gap8-12XX-gru8`, 1XX + 2XX; `rpr-rgb-gap8-123XX-gru8`, 1XX + 2XX + 3XX). The anchor network is a second RPRNet on (keyframe, frame) RGB-D pairs with coarse correlation and a frozen encoder (`runs/anchor-rgbd-e20`, 2XX; `anchor-rgbd-23XX`); session adaptation fine-tunes it on pairs within the new room scan (5 epochs, lr 1e-4).

**Tracker-free map (deployment, untested):** in a new room the room-scan poses must come from the scan itself (SLAM, or classical odometry + PnP loop closures over the room scan, or a feed-forward model such as StreamVGGT). Evaluate in this room: build the map without the Polaris, align once to the Polaris (residual = map error), anchor the sweeps against it. This is the last test-time use of the Polaris.

## 3. Accuracy, metrics and evaluation rules

- **Physics:** elevational beam width 1–2 mm, so error much beyond 2 mm blurs the volume. At 9 cm imaging depth 1° moves the image bottom by 1.6 mm. **Drift is the central risk:** a systematic 0.01 mm per frame adds up to 6 mm over 600 frames; hence anchors.
- **Label noise:** Polaris ~0.1–0.25 mm per frame; tracker at 20 Hz, interpolated; tracker clock offset measured with the camera gyro and corrected (§5).
- **Main metric:** mean pixel error over the US image after compounding (all 640 × 480 pixels via the US calibration), plus Dice of the compounded volume; also the median error at points on the US image (anchoring tables), per-step error against zero motion, drift (final error / path length) and maximum error. TUS-REC metrics for the US comparison (`us_only/`).
- **Rules:** per sweep, bootstrap intervals over sweeps (not frames); segments split where the marker is lost (no ground truth); each segment starts at the true pose unless `--start anchor`; settings chosen on validation (2XX run-205, run-211), test collections (3XX, 4XX) run once. Validation inside a training session flatters learned models (§6.1): hold out whole sessions.

## 4. Calibration and units

`T_a_b` maps points from frame b into frame a; millimetres throughout. Hand-eye `.npy` units always given explicitly (`--hand-eye-units`); `pose_units` per run in `record_config.json`, checked by the dataloader.

**Hand-eye `T_marker_cam.npy` (= `T_marker_cam_2XX.npy`): calib_201 + calib_202 merged, 9 Oct 2026.** ChArUco 12×9 squares, 15 mm squares, 11.25 mm markers, DICT_5X5, fixed in the room for both sessions; `tools/merge_hand_eye.py` fits one hand-eye and one board pose to the **still frames** (< 5°/s) of both sessions. Board-corner error 3.5 mm (cross-session 3.6 / 4.2 mm); translation (−99.7, 4.8, 77.1) mm, lever 126 mm; calib_104 + 105 (8 Oct, other board) agree within 1.6 mm, 0.8°. Valid for 1XX–4XX (nothing dismounted). **Never solve on all frames into `T_marker_cam.npy`** (an all-frames solution was 22 mm off).

**US calibration `T_marker_us.npy` + `S_us_px_to_mm.npy`** (0.2294 × 0.2210 mm/px): N-wire phantom by Li Qi (UCL), with our marker on our probe, scanner settings as recorded (`us_calibration.json`, `calib_matrix.csv` in TUS-REC format). Pixel → world: `T_world_marker @ T_marker_us @ S @ [u, v, 0, 1]`, pixels 1-based on the native 640 × 480 image = our crop [121, 80]–[619, 440] of the 800 × 600 screen grab (checked against TUS-REC scans within 1–4 px).

## 5. Data and recording

**TUS-REC reference scans** (`data/tusrec/`, two forearm scans, 572 and 511 frames, extracted to `data/tusrec/jpg/`; side by side with ours: `data/tusrec/compare_tusrec_vs_ours.jpg`): same image grid and fan geometry at the top (width at row 100: 121–517 vs 122–517 px; `calib_matrix.csv` scale within 0.07 %), but our fan fades at depth and at the sides (signal at row 400: x 340–460 vs 85–554 px; contact, gel or anatomy) and our crop contains static screen overlays (depth-marker dots, orientation dot), masked in compounding.


**Collections** (`data/train_<NXX>`; room scans `room-NXX`, sweeps `run-NXX`, hand-eye sessions `data/calib/calib_NXX`, numbered in recording order; combined training via folders of links, e.g. `data/train_12XX`; the next collection is `5XX`):

| Data | What | Problem | Use |
|---|---|---|---|
| **1XX** (`room-101`, `102`, `run-101`…`112`) | 8 Oct: 2 room scans, 12 sweeps | depth wrong (cable in front of the depth sensor); marker lost often (~20 % of frames) | extra RGB odometry training data only |
| **2XX** (`room-201`, `202`, `run-201`…`212`) | 9 Oct: 2 room scans (3 min), 12 sweeps | none found | main training set; validation `run-205`, `run-211` |
| **3XX** (`room-301`, `302`, `run-313`…`317`) | 9 Oct, same room, a few small objects moved: 2 room scans, 5 sweeps | none found | first test set (own room scan, and 2XX scan = scene change) |
| **4XX** (`room-401`…`406`, `run-401`…`428` without 417, 422) | 14 Oct, blocks A–E below: 6 room scans, 26 sweeps, a second subject | room scans short (40 s, except room-401) and held low: they cover 0–14 % of the sweep viewpoints (§6.3); sweeps slower than 2XX (6–18 mm/s) | held-out test; fair for odometry and for classical anchors, a poor-room-scan case for the anchor network |

| 4XX block | What | Room scans | Sweeps |
|---|---|---|---|
| A | new session, subject 1 | `room-401` (90 s), `room-402` (40 s) | `run-401`…`408` |
| B | small rearrangement (box, bottles moved, a mouse on the table) | `room-403`, `404` | `run-409`…`412` |
| C | large rearrangement (bowl-shaped object removed, pelvis model, bottle, box, paper roll moved) | `room-405`, `406` | `run-413`…`416` |
| D | subject 2, room as in C | C's | `run-418`…`421`, `423`, `424` (an arm briefly in view in 419–421) |
| E | occlusion, subject 2 | C's | `run-425`, `426` (arm across the view, 22–29 % of the time); `run-427` (= former 422), `428` (= former 417): incidental |

Recording checks for 4XX: all streams clean, pose clock offset +5 to +25 ms (gyro correlation ≥ 0.98), marker lost ≤ 0.35 s, scanner settings as 2XX/3XX (Depth 9 cm, gain 48 %, 19 fps, Map 1, zoom 100 %). Occlusion appears in depth as a no-depth region (the arm is closer than the sensor's minimum range).

**Pipeline (recorder layout 2).** `tools/record_train.py` saves every stream separately (RGB, raw depth, US screen grab, IMU, Polaris pose) with header and receive stamps. `tools/match_streams.py` builds `frames.csv` offline:
- raw depth aligned to RGB (3×3 splat); nearest depth (±20 ms) and US frame (±35 ms; the grabber delivers ~25 frames/s with ~25 % repeats, flagged `us_repeat`);
- Polaris pose deduplicated (20 Hz, republished 3× at 60 Hz), interpolated at the RGB stamp; clock offset from tracker vs gyro angular speed, corrected with `--apply-sync`;
- probe in the air at the start/end flagged `us_air` (0.2–3 s of placing the probe; skipped); marker loss `pose_lost`.
- US crop per run in `us_roi.json` (excludes the scanner clock); recorded files are never edited.

**Protocol for the next collection** (lessons from 4XX):
- Lock RGB exposure / white balance and the scanner settings for the whole collection; keep cables and hands away from the camera; do not remount marker or camera after the hand-eye calibration.
- **Room scan right before the sweeps, ~2 × 90 s, dense, several passes, from where the probe camera points during the sweeps (same area, heights, angles); nothing moves in between. Check coverage after the first sweep** (`tools/check_coverage.py`: ≥ 80 % of sweep frames need a room-scan pose within 30 mm and 10°; 2XX/3XX: 86–93 %, 4XX: 0–14 %).
- Sweeps: variety (straight / C / S patterns, probe perpendicular and parallel to the path, sideways translation, tilting, rocking), 3–15 mm/s, continuous 20–60 s, some closed loops; marker visible > 95 %; camera on textured static content; some probe rotation (for the clock-offset estimate). Decide the test sweeps in advance.

```bash
# 1. hand-eye (only after dismounting): two sessions, board fixed, slow motion with pauses
B="--squares-x 12 --squares-y 9 --square-mm 15 --marker-mm 11.25 --dict DICT_5X5_1000"
python3 tools/record_calibration.py --run calib_501 --root ./data/calib --duration 90
python3 tools/record_calibration.py --run calib_502 --root ./data/calib --duration 90
python3 tools/merge_hand_eye.py --runs calib_501 calib_502 --out T_marker_cam_5XX.npy $B
# 2. room scan, 3. sweeps (+ sweep log), coverage check after the first sweep and at the end
python3 tools/record_train.py --run room-501 --root ./data/train_5XX --no-us --duration 120
python3 tools/record_train.py --run run-501 --root ./data/train_5XX --duration 60 --no-match
python3 tools/check_coverage.py --root data/train_5XX --scans room-501 room-502 --sweeps run-501
# 4. matching (training PC)
python tools/match_streams.py data/train_5XX/* --apply-sync
```

## 6. Results

### 6.1 Learned system: RPRNet odometry + anchor network (9–13 Oct)
Fixed split: train 2XX (+ 1XX for odometry), validate run-205 / run-211, test 3XX once. Two data fixes were needed first: trimming the probe-in-air start (`us_air`; otherwise every trajectory started 50–180 mm off) and a 35 ms US tolerance (25 ms dropped 5–13 % of rows).

| 3XX test (5 sweeps), mean | per-step translation / rotation vs zero motion | drift | US-image error, median: no anchors → pose graph | pixel error / Dice | anchor error |
|---|---|---|---|---|---|
| final system, own room scan | −26 / −79 % | 23 % | 37.5 → 13.6 mm [10.3, 16.2] | 13.9 mm / 0.84 | 15.3 mm |
| + session adaptation on the room scan | | | 37.5 → **8.5 mm** [7.1, 10.0]; live 8.7 | **8.5 mm / 0.91** | 7.8 mm |
| outdated 2XX room scan (scene change) | | | 37.5 → 42.2 mm (worse than none) | 42.2 mm / 0.48 | 39.8 mm |
| 2XX validation (2 sweeps) | −58 / −85 % | 4.2 % | 17.0 → 7.1 mm | 7.7 mm / 0.86 | 6.5 mm |

- **Chosen odometry** (validation only): frame gap 8 + bidirectional GRU over 8-frame windows + weight averaging (max error 57.7 → 38.8 mm vs gap 4 pairs); a motion-weighted loss and depth input gave no gain; 1XX + 2XX vs 2XX only: small gain; per-step translation keeps improving with more training sweeps (5 / 10 / 20: −23 / −25 / −38 %). Anchor settings: every 1 s, 3 keyframes, 20 epochs; oracle retrieval changes little (17.0 → 16.5 mm).
- **Session effect:** within a training session anchors are ~4–8 mm, in a new session 15–20 mm; with 3XX sessions in training, run-315 drops from 43 % to 11 % drift and anchors from 20 to 4 mm. The networks learn the session, not the geometry; odometry does not overfit (far above the label-noise floor), the anchor network does (train 3.1 vs validation 8.1 mm).
- **Sideways translation** was never learned (no better than zero motion); rotation was (−74 to −90 %).

### 6.2 4XX with the learned system (15 Oct)
Models trained on everything before 4XX (`rpr-rgb-gap8-123XX-gru8`, `anchor-rgbd-23XX`), adaptation per block. **Odometry held** (per step −31 to −41 % / −76 to −80 % vs zero motion; drift 13–22 %; US-image error 29–39 mm median). **Anchoring failed in every block:** anchor errors 25–100 mm, results 30–58 mm (median), worse than no anchors; start from the anchors 30–110 mm off.

### 6.3 Why 4XX anchoring failed: room-scan coverage
From the Polaris poses alone (`tools/check_coverage.py`):

| | sweep frames with a room-scan pose within 30 mm and 10° | best room-scan view per sweep frame (median) | nearest room-scan position, any angle |
|---|---|---|---|
| 2XX / 3XX | 86 % / 93 % | 29 mm, 2.5° (3XX) | 6 mm (3XX) |
| 4XX A–E | 0–14 % | 65–128 mm, 3–9° | 28–64 mm |

The anchor network's error grows with the keyframe distance (adapted, median: 3XX 5.6 / 7.5 / 10.6 mm at 0–20 / 20–40 / 40–60 mm; 4XX 19 / 16 / 33 mm, and 45–57 mm beyond 60 mm, where 78 % of the 4XX anchors fell, against 9 % in 3XX). A smaller session gap remains (2× at the same distance).

### 6.4 Why a changed room breaks the anchor network (`tools/anchor_saliency.py`, `runs/saliency/`)
Changed pixels found without labels (frame moved into the keyframe with true poses and depth; depth disagrees by > max(30 mm, 3 %)); gradient × input attribution of the pair error; masking test (changed pixels blanked vs the same mask shifted).

| | 3XX, own room scan | 3XX, outdated 2XX room scan |
|---|---|---|
| pair error at the same keyframe distance (15–45 mm) | 14.5 mm | **40.7 mm** |
| share of the frame that changed | 10 % (detector floor: parallax, wall noise, hands) | **28 %** |
| look ratio (attribution on changed pixels / their area) | 1.30 | 1.26 |
| pairs better when the changed pixels are blanked | 13 % | 2 % |

The scene change causes the error, but the network does not single out the moved objects, and removing them does not help: it regresses one pose from the whole comparison and **has no way to reject part of the image as outliers.** Reject rules based on its own outputs do not fix this (best: keyframe-estimate spread ≤ 15 mm, 3XX 13.6 → 12.6 mm, outdated scan 42.2 → 40.8 mm, still worse than no anchors).

### 6.5 Classical odometry and anchors (19–20 Oct; `runs/anchoring-classical-*`, `runs/classical/`)

**Anchors on the same (keyframe, frame) pairs:**

| | anchor network | classical (SIFT + PnP-RANSAC with depth) | pairs solved |
|---|---|---|---|
| 3XX, own room scan | 15.7 mm / 1.04° | **3.2 mm / 0.37°** | 100 % |
| 3XX, outdated 2XX room scan | 42.6 mm / 1.47° | **12.0 mm / 0.60°** | 96 % |
| 4XX B, own room scan (poor coverage) | 24.2 mm / 1.35° (adapted) | **3.8 mm / 0.29°** | 100 % |

**Odometry on the same steps** (no anchors):

| | step error, translation / rotation | drift | max error | steps solved |
|---|---|---|---|---|
| RPRNet, 3XX ; 4XX | 1.9 mm / 0.16° ; 1.2–2.1 mm / 0.11–0.23° | 23 % ; 13–22 % | 68 ; 61–98 mm | – |
| **classical**, 3XX ; 4XX | **0.8 mm / 0.09° ; 0.7–1.2 mm / 0.07–0.12°** | **6.7 % ; 1.9–4.1 %** | **19 ; 20–26 mm** | 100 % (also under occlusion) |

**Full system** (mean pixel error at the US image / Dice; anchor error median in brackets):

| | classical odometry only | classical anchors + RPRNet | **classical anchors + classical odometry** | same, start from the anchors | outdated room scan (classical anchors + RPRNet) |
|---|---|---|---|---|---|
| 3XX | 10.1 / 0.88 | 6.2 / 0.93 (2.8) | **3.3 / 0.95** (2.6) | 3.2 | 11.4 / 0.88 (10.4), 2XX scan |
| 4XX A, new session | 14.5 / 0.84 | 8.0 / 0.89 (5.0) | **4.6 / 0.92** (5.3) | 4.4 | – |
| 4XX B, small rearrangement | 11.1 / 0.86 | 5.4 / 0.91 (3.1) | **3.6 / 0.94** (3.2) | 3.7 | 8.5 / 0.86 (7.9), A's scan |
| 4XX C, large rearrangement | 9.9 / 0.87 | 6.1 / 0.91 (5.8) | **5.2 / 0.92** (5.9) | 5.3 | 33.8 / 0.76 (80, 21 % accepted), A's scan |
| 4XX D, subject 2 | 13.1 / 0.83 | 7.5 / 0.89 (7.0) | **7.0 / 0.89** (7.1) | 7.2 | – |
| 4XX E, occlusion | 13.7 / 0.84 | 8.0 / 0.90 (5.6) | **5.1 / 0.91** (5.2) | 5.3 | – |

- Best everywhere with nothing trained; the anchors (2.6–7 mm) are now the floor, plus hand-eye (3.5 mm corner error) and US calibration.
- Classical anchors work with the short 4XX room scans and a small room change, not a large one.
- Starting from the anchors costs nothing (≤ 0.2 mm): no Polaris needed at the start of a sweep.
- Pose-graph anchor sigma on 2XX validation: 11 mm / 1° (kept) 4.2 mm, 5 mm / 0.5° 4.2 mm, 3 mm / 0.3° 4.4 mm. Classical odometry has a weak stretch in run-205 (11.6 % drift).

### 6.6 SCR anchors (20 Oct; `runs/scr-*`, `runs/anchoring-scr-*`)

| | SCR anchors, every 1 s, median / p90 (100 % solved) | classical anchors | SCR anchors + classical odometry (pixel error / Dice) |
|---|---|---|---|
| 3XX | 9.8 / 22.1 mm | 2.6 mm | 6.5 / 0.92 |
| 4XX A / B / C | 17.7 / 16.0 / 21.8 mm | 5.3 / 3.2 / 5.9 mm | 16.3 / 12.0 / 15.6 |
| 4XX D / E (C's model) | 26.0 / 22.1 mm | 7.1 / 5.2 mm | 21.4 / 16.5 |
| B, C with A's model (outdated room scan) | 50.3 / 55.3 mm | 7.9 / 80 mm | 48.6 / 58.2 |

Better than the regression anchor network, 3–5× worse than classical; on 4XX worse than classical odometry alone. **It underfits:** 24–28 mm room-coordinate error even on its training frames after 15 epochs. Possible fixes: longer training, finer grid / higher resolution, depth as input, per-pixel confidence, ACE-style pixel-shuffled training.

**3D pages** (`runs/volume3d/classical_scr/`, 3XX run-313…317, 4XX run-405, 410, 414, 419, 426): true poses vs classical anchors + classical odometry, SCR anchors + classical odometry, classical odometry only, RPRNet only. Mean pixel error per page, e.g. run-426 (occlusion): 3.6 / 11.6 / 13.5 / 78.4 mm.

### 6.7 US (13–14 Oct; `us_only/`, `runs/li-baseline/`)

| 3XX test, TUS-REC metrics | global pixel error | final pixel error | drift |
|---|---|---|---|
| zero motion | 58.0 mm | 58.9 mm | 20.2 % |
| Li et al. (US only, trained on 2XX) | 60.3 mm | 97.8 mm | 37.0 % |
| ours, US-only motion branch | 41.8 mm | 48.9 mm | 17.2 % |
| ours, RPRNet RGB odometry | 38.7 mm | 58.1 mm | 18.6 % |
| ours, RGB + US | 38.2 mm | 43.9 mm | 16.4 % |
| ours, RGB odometry + adapted anchors | 8.6 mm | 15.2 mm | 4.6 % |

- The US motion branch (own EfficientNet, per-image standardisation, difference + correlation; `train.py --use-us --us-mode motion`, `--no-rgb`) learns translation, not rotation; RGB + US gives no overall gain. Li et al. reaches 30.7 mm within the training session but is no better than zero motion in a new one. Pose-level fusion (best weight 0 = no fusion) and bridging camera blackouts with US (40.6 vs 41.5 mm zero motion) do not help.
- Probable reasons: US got the RGB step (too large for speckle decorrelation), downsampled to 240 × 320, camera-motion targets instead of image-plane motion, little temporal context, one subject.
- **Not used in any final system.** With a 3–7 mm camera pose, US no longer has to estimate motion from scratch, only refine it locally (§8).

### 6.8 Literature
- **MambaVO (arXiv 2412.20082):** state-of-the-art deep VO is not pose regression but learned matching (EfficientLoFTR, DINOv2) + PnP initialisation + learned match weights + differentiable bundle adjustment; it reports that direct pose regression generalises poorly, and that a learned matcher beats SIFT in the same pipeline.
- **StreamVGGT (arXiv 2507.11539):** streaming feed-forward pose, depth and point maps; a candidate for the tracker-free room-scan map and a robust start pose, at general-reconstruction (not mm) accuracy.

### 6.9 Ablations: anchor interval and anchors only (20 Oct; `runs/ablation-*`, `tools/run_ablations.sh`)
Classical anchors; median US-image error (mm) after the pose graph, and the mean step-to-step change of the error in brackets (jitter, lower = smoother); mean pixel error / Dice where exported.

**Anchor interval** (∞ = odometry only):

| | 0.5 s | 1 s | 2 s | 5 s | ∞ |
|---|---|---|---|---|---|
| classical odometry, 3XX | 2.9 | 3.2 | 3.2 | 4.6 | 9.5 |
| — mean pixel / Dice | 3.2 / 0.95 | 3.3 / 0.95 | 3.5 / 0.95 | 4.7 / 0.93 | 10.1 / 0.88 |
| classical odometry, 4XX A / B / C | 4.1 / 3.2 / 4.1 | 4.2 / 3.4 / 4.6 | 4.1 / 3.5 / 4.8 | 4.3 / 4.1 / 5.9 | 15.2 / 11.3 / 8.9 |
| classical odometry, 4XX D / E | 6.0 / 4.5 | 6.3 / 4.8 | 6.6 / 5.4 | 7.1 / 6.6 | 12.7 / 13.0 |
| — 4XX A–E mean pixel | 3.4–6.6 | 3.6–7.0 | 4.0–7.4 | 4.9–8.0 | 9.9–14.5 |
| — RPRNet odometry, 3XX mean pixel / Dice | 5.2 / 0.93 | 6.2 / 0.93 | 7.7 / 0.92 | 10.6 / 0.89 | 38.5 / 0.61 |
| RPRNet odometry, 3XX: pose graph / offline correction | 5.0 / 3.0 | 5.7 / 3.0 | 7.3 / 4.0 | 9.8 / 6.8 | 37.5 |

**Anchors only** (no odometry, a classical anchor every step, ~0.27 s) vs anchors every 1 s + classical odometry:

| | anchors only, raw | anchors only, smoothed (pose graph) | anchors 1 s + classical odometry |
|---|---|---|---|
| 3XX: median (jitter) | 2.9 (3.03) | 4.4 (1.62) | 3.2 (1.09) |
| 3XX: mean pixel / local (step) pixel error / Dice | 3.7 / 2.06 / 0.94 | 6.0 / 1.11 / 0.87 | 3.3 / 0.73 / 0.95 |
| 4XX A: mean pixel / local / Dice | 5.8 / 2.76 / 0.88 | 6.9 / 1.02 / 0.88 | 4.6 / 0.76 / 0.92 |
| 4XX A–E: median (jitter) | 3.1–7.1 (1.96–5.64) | 4.1–7.4 | 3.4–6.3 (1.13–1.57) |
| 4XX A–E: mean pixel / local pixel error | 3.5–8.6 / 1.29–4.41 | 5.4–7.8 / 0.88–1.45 | 3.6–7.0 / 0.74–1.32 |

- **Odometry alone drifts:** removing the anchors raises the error 2–4× with classical odometry and 7× with RPRNet; the error grows smoothly with the anchor interval.
- **Good odometry makes anchors cheap:** with classical odometry, anchors every 2 s cost ≤ 0.6 mm and every 5 s 1–2 mm against every 1 s; with RPRNet odometry the error rises fast with the interval (pose graph 5.0 → 9.8 mm from 0.5 to 5 s).
- **Anchors alone are as accurate in the median but jittery:** the step-to-step error is 2–4× larger (local pixel error 2.1–2.8 vs 0.7–0.8 mm), which blurs the volume; smoothing them without odometry costs accuracy (3XX 3.7 → 6.0 mm); they need 4× more anchor computations and have no fallback when an anchor fails. Both parts are needed.
- With RPRNet odometry the pose graph is worse than the simple offline correction (anchor sigma chosen for network anchors); with classical odometry the two are equal.

## 7. Risks and limitations

- **Classical method:** needs texture and a mostly unchanged room (large rearrangement: 80 mm anchors); depends on RealSense depth (missing below ~20–30 cm and on dark or shiny surfaces, noise growing with distance); SIFT on CPU ~0.1–0.3 s per frame (fine for anchors at 1/s, not for 30 Hz odometry); fixed thresholds; only the inlier count as confidence; weak stretches possible (run-205: 11.6 % drift).
- **Room scan:** must cover the sweep viewpoints (check while recording); a large room change requires a new scan.
- **Map without a tracker** (§2): untested; its error is a floor on anchoring in a new room.
- **Accuracy floor above 2 mm:** anchors 2.6–7 mm, hand-eye 3.5 mm, US calibration; all evaluations are one room.
- **Occlusion:** partial occlusion is handled (RANSAC uses the rest of the view); a fully covered camera is not tested.
- **One room, two subjects;** room-to-anatomy registration is needed for cross-session navigation; limbs move between sweeps.

## 8. Next steps

1. **Done (§Summary, §6.9):** fair table complete; anchor interval; anchors only (`tools/run_ablations.sh`), all exported.
5. **US as local refinement** of the camera pose: US-to-US registration of overlapping frames as pose-graph constraints (out-of-plane), volume self-consistency, registration to anatomy.
6. **Tracker-free room-scan map** (§2), then a new collection (5XX) with checked coverage.
7. **Learned matcher** (LightGlue / EfficientLoFTR, fine-tuned on our data with Polaris + depth correspondences) and a better SCR (§6.6), for large room changes and low texture.

## 9. Code map

| File | Purpose |
|---|---|
| `dataloader.py`, `model.py`, `loss.py`, `train.py` | RPRNet odometry: data (skips marker-lost and probe-in-air frames), model (optional US motion branch, coarse correlation for anchors), loss, training (`--val-runs`, `--temporal gru`, `--swa-epochs`) |
| `trajectory.py`, `eval.py`, `diagnostics.py` | chaining, per-step and trajectory metrics, prediction cache `<arm>/preds/`; bias / noise / drift diagnostics |
| `poses.py` | per-frame pose export (JSON), US compounding and its metrics (pixel error, Dice); `--source model / zero / anchored-… / classical-vo-…` |
| `anchoring.py` | `pairs`, `train` (anchor network, session adaptation), `evaluate` (`--anchor network / classical / scr`, `--odometry-source model / zero / <cache>`, `--start anchor`, `--pgo`, `--map-root/--map-scans`, `--accept-spread`, `--max-key-dist`, `--interval`), `coverage`, `simulate` |
| `scr.py` | SCR anchors: `train` per room scan, `eval` |
| `tools/run_ablations.sh` | the §8 evaluation runs (fair-table gaps, anchor interval, anchors only) and their US-image exports |
| `tools/anchor_classical.py` | classical solver (`pnp_pose`); classical vs network anchors on the same pairs; depth agreement |
| `tools/classical_odometry.py` | classical odometry on the network's steps; `classical-vo-<test>` caches; comparison table |
| `tools/anchor_saliency.py` | attribution and masking test of the anchor network |
| `tools/check_coverage.py` | room-scan coverage of the sweeps from raw poses (GO / NO-GO) |
| `tools/record_train.py`, `tools/match_streams.py` | recording and offline matching |
| `tools/record_calibration.py`, `tools/calibrate_hand_eye.py`, `tools/validate_hand_eye.py`, `tools/merge_hand_eye.py` | hand-eye calibration |
| `tools/report_results.py`, `tools/learning_curves.py`, `tools/motion_analysis.py` | per-sweep tables with bootstrap intervals; learning curves; error by motion type |
| `tools/volume_3d.py`, `tools/volume_viewer.py` | interactive 3D page of a compounded sweep (`--labels`); slice viewer |
| `tools/draw_diagram.py`, `tools/draw_scr_diagram.py` | diagrams: RPRNet system, SCR anchors |
| `us_only/`, `tools/export_tusrec.py` | US-only: Li et al. evaluation, TUS-REC metrics for our models, pose-level fusion; export in TUS-REC format |
| `geometry.py`, `inspect_data.py` | SE(3) helpers; data diagnostics per recording |

Results index: `runs/README.md`. Short summary and data guide for other projects (e.g. an SCR approach): `HANDOFF_SCR.md`. Per-sweep tables of the learned system: `runs/reports/`.





On the training PC:


git pull
EXPORT_ONLY=1 nohup bash tools/run_ablations.sh > ablations_export.log 2>&1 &
tail -f ablations_export.log          # wait for "=== done" (skipped ones say "done already")
git add runs ablations_export.log
git commit -m "Ablation exports"
git push