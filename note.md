# US_SCR: scene coordinate regression anchors for markerless US probe tracking

Status 21 Oct 2026. Merges the project brief (old `note.md`) and the data guide (`HANDOFF_SCR.md`, from rgbd-us) and adds the SCR results so far. Source project: `rgbd-us` (`note_RPR.md` there has every detail).

## 1. Problem and goal

A probe-mounted RGB-D camera (Intel RealSense D435i, colour 1280 × 720) looks at the room; an NDI Polaris marker on the probe gives ground truth (~0.25 mm). The goal is the probe pose of every US frame with nothing outside the probe. Target: **~2 mm at the US image**, which lies ~16 cm from the camera (1° of rotation ≈ 1.6 mm at the image bottom).

The system has three parts: **odometry** between frames; **anchors**: absolute poses against a room scan recorded with the same camera before the exam; an offline **pose graph** that combines them. Both are needed: odometry alone drifts (2–7 % of the path for classical, 13–23 % for learned); anchors alone are accurate but jump from step to step. With good odometry, an anchor every 1–2 s is enough.

This project replaces the anchors with **scene coordinate regression (SCR)**: a network predicts the room coordinate of every image cell, and PnP-RANSAC turns those correspondences into a pose. Questions it has to answer:
- why the first SCR underfit, and how far fixing it closes the gap to classical anchors;
- whether SCR can match SIFT + depth + PnP-RANSAC at the mm scale in an unchanged room;
- where it could beat it: large room changes, low texture, speed, no keyframe retrieval or pose prior.

## 2. What rgbd-us found

| mean error at the US image | 3XX (5 sweeps) | 4XX (blocks A–E) |
|---|---|---|
| classical odometry + classical anchors (SIFT + PnP-RANSAC with depth) | **3.3 mm** | **3.6–7.0 mm** |
| classical odometry only | 10.1 mm | 9.9–14.5 mm |
| classical odometry + first SCR anchors | 6.5 mm | 12.0–21.4 mm |
| learned odometry + learned anchor network (pose regression) | 13.9 (8.5 adapted) mm | failed: 26–58 mm |

**Anchor accuracy** (camera position error, one frame every 1 s; the number SCR competes on):

| | 2XX val (run-205, 211) | 3XX | 4XX A / B / C | 4XX D / E (C's map) | outdated map: 2XX→3XX / A→B / A→C |
|---|---|---|---|---|---|
| classical anchors (median / p90) | 5.2 / 11.9 mm, 0.33° | 2.6 / 6.9 mm, 0.34° | 5.3 / 3.2 / 5.9 | 7.1 / 5.2 | 10 / 8 / 80 mm (C: 21 % accepted) |
| first SCR (`rgbd-us/scr.py`) | 15.8 / 31.3 mm (rerun here) | 9.8 / 22.1 mm | 17.7 / 16.0 / 21.8 | 26.0 / 22.1 | — / 50.3 / 55.3 |
| anchor network (pose regression) | | 15 mm | 25–100 mm | | |

Per sweep, classical: run-205 6.5 / 15.6, run-211 3.9 / 8.3 mm; 3XX run-313…317 3.1, 2.7, 2.5, 1.9, 3.0 mm.

Note on comparing with classical: classical anchors are evaluated at the anchor times of the odometry chain (28 per 3XX sweep), retrieve 3 room-scan keyframes **near the odometry pose** (median 28–31 mm away) and average them; the numbers are the mean of per-sweep medians. SCR is evaluated every 30 usable rows (29 per sweep), with no prior, pooled. For classical the two aggregations agree (3XX pooled 2.64 vs mean 2.6 mm), the frame sets differ slightly.

**Lessons**
- **Direct pose regression does not generalise to a new session.** The networks learn the session, not the geometry, and cannot reject outliers (moved objects, hands).
- **The motion is tiny:** 2–5 mm per step, a sweep path of ~0.3–1 m within a few tens of cm, the camera 0.5–2.5 m from the scene. A learned regressor's error floor (~1–2 mm, 0.1–0.2° per step) is as large as the motion. Precision has to come from a geometric solve over many accurate correspondences. Public benchmarks (7-Scenes, TUM, KITTI) work at the cm–m scale and cannot show this.
- **Anchors need room-scan coverage of the sweep viewpoints:** 3XX covers 93 % of the sweep frames (a room-scan pose within 30 mm and 10°), 4XX only 0–14 % (`rgbd-us/tools/check_coverage.py`).
- **Room changes:** classical anchors survive a small change (8 mm) but fail on a large one (80 mm). The first SCR failed on both (50–55 mm).

## 3. Data

**Where**
- Training PC (RTX A4500, 20 GB): `/data2/u0137815/rgbd-us/data/train_<NXX>/`, all collections matched; rgbd-us repo at `/data2/u0137815/rgbd-us`. `data/test_4XXA` … `test_4XXE` are folders of links into `train_4XX`.
- This machine (RTX 3050, 4 GB): `~/Desktop/rgbd-us/data/`, mostly unmatched raw data; only `train_3XX/run-316` has a `frames.csv`. Use `~/anaconda3/envs/gpu/bin/python` (the default `python3` has torch 1.5).

| collection | room scans | sweeps | role |
|---|---|---|---|
| 1XX (8 Oct) | room-101, 102 | run-101…112 | **do not use**: depth wrong (cable in front of the sensor), marker often lost |
| 2XX (9 Oct) | room-201, 202 (3.0 min; 5,366 usable frames) | run-201…212 (9.9 min) | main session; **validation sweeps run-205, run-211** |
| 3XX (9 Oct) | room-301, 302 (2.0 min) | run-313…317 (2.5 min) | **the clean test:** same room as 2XX, a few small objects moved |
| 4XX A (14 Oct) | room-401 (90 s), 402 (40 s) | run-401…408 | new session |
| 4XX B | room-403, 404 (40 s each) | run-409…412 | small rearrangement |
| 4XX C | room-405, 406 (40 s each) | run-413…416 | large rearrangement |
| 4XX D | C's scans | run-418…421, 423, 424 | second subject |
| 4XX E | C's scans | run-425…428 | occlusion (arm in view) |

**Files per run**

| file | content |
|---|---|
| `frames.csv` | one row per RGB frame (~30 Hz); use this table |
| `rgb/NNNNNN.png` | colour 1280 × 720 (OpenCV reads BGR) |
| `depth/NNNNNN.png` | depth **aligned to the RGB image**, uint16, 1280 × 720, **mm**, 0 = invalid; reliable ~100–3000 mm |
| `depth_raw/` | the depth sensor's own 848 × 480 images; ignore |
| `camera_info.json` | RGB intrinsics `K` (fx ≈ 919.8, fy ≈ 919.5, cx ≈ 652.9, cy ≈ 373.6), no distortion; the same camera for all runs |
| `us/`, `us_roi.json` | US screen grabs 800 × 600, crop [121, 80]–[619, 440] (sweeps only) |
| `match_report.json` | matching quality: `pose_offset_ms` (already applied), `pose_lost`, `us_air_s` |

`frames.csv` columns: `timestamp` (RGB time, s); `rgb`, `depth`, `us` (paths relative to the run folder); **`tx, ty, tz`** (mm) and **`qx, qy, qz, qw`** (scalar last) = `T_world_marker` in the Polaris frame, interpolated at the RGB time with the clock offset corrected — **empty = marker lost, skip the row**; `us_air` = 1: probe not yet on the skin; `us_repeat`: the US frame repeats the previous one.

**Camera pose:** `T_world_cam = T_world_marker @ T_marker_cam`, world = Polaris frame (it did not move between 2XX and 3XX). **`T_marker_cam.npy` must be the rgbd-us one** (4 × 4, mm, valid for 1XX–4XX, board-corner error 3.5 mm); this repo's copy was replaced on 21 Oct — the old one was 17.7 mm / 3.6° off.

```python
import json, cv2, numpy as np, pandas as pd
from scipy.spatial.transform import Rotation as R

run = "/data2/u0137815/rgbd-us/data/train_3XX/room-301"
df = pd.read_csv(f"{run}/frames.csv").dropna(subset=["tx"])          # rows with a Polaris pose
K = np.array(json.load(open(f"{run}/camera_info.json"))["K"]).reshape(3, 3)
T_mc = np.load("T_marker_cam.npy")                                    # marker -> camera, mm

r = df.iloc[0]
T_wm = np.eye(4); T_wm[:3, :3] = R.from_quat([r.qx, r.qy, r.qz, r.qw]).as_matrix(); T_wm[:3, 3] = [r.tx, r.ty, r.tz]
T_wc = T_wm @ T_mc                                                    # camera pose in the room (mm)

z = cv2.imread(f"{run}/{r.depth}", cv2.IMREAD_UNCHANGED).astype(np.float64)   # mm, aligned to rgb
v, u = np.nonzero((z > 100) & (z < 3000))
X = np.stack([(u - K[0, 2]) / K[0, 0] * z[v, u], (v - K[1, 2]) / K[1, 1] * z[v, u], z[v, u], np.ones(len(u))])
scene_coords = (T_wc @ X)[:3].T                                       # SCR labels: room coordinate (mm) of pixel (u, v)
```

**Camera: D435i** (inferred: colour FoV 69.7° × 42.8°, depth 848 × 480 at ~90°, depth-to-colour offset 14.6 mm, IMU stream). 50 mm stereo baseline, so depth noise grows ~ with distance²: under ~2 % at 2 m by spec, mostly along the ray.

**Label quality:** room points from one frame re-projected into a frame 1 s later agree with that frame's depth within 7.9 mm (median) at 1–1.5 m, i.e. ~5–6 mm per label. The 3.5 mm hand-eye error makes labels **view-dependent** (the same wall point gets slightly different coordinates from different probe orientations). Classical anchors largely cancel this by chaining off a keyframe ~30 mm away; a single global SCR map has to average it — a likely floor for SCR.

**Label hygiene (not applied yet):** use 100 < depth < 3000 mm; down-weight far pixels (1/z²) or cap at ~2 m; drop depth edges (3×3 neighbourhood spanning > ~3 % of the depth); never train on hands/arms (< 300 mm), the operator's sleeve (4XX D/E) or the subject.

**Quirks:** `record_config.json` in 3XX still carries old run names (run-316 says `run-216`), trust the folder name; in 4XX, run-427 was run-422 and run-428 was run-417.

## 4. Test protocol (identical to `rgbd-us/scr.py eval`)

- Map on a session's **room scans only** (the deployment case). Extra mapping data (other sweeps of the same session, never the test sweep) only as a separately labelled experiment.
- Test on the sweeps: **one frame every 30 usable rows** of `RPRDataset` (Polaris pose, not in the air, US frame and full-size depth present).
- PnP-RANSAC 10 px (full resolution), ≥ 30 inliers. Report camera position error (mm) and rotation (°), median and p90, share solved; `scr_anchor.py` also gives the mean of per-sweep medians, inliers and ms per frame, with a fixed RANSAC seed per frame.
- **Settings are chosen on 2XX validation only** (map room-201/202 → run-205, run-211). 3XX and 4XX only report.
- Splits: clean 3XX→3XX; new sessions 4XX A–E (D, E use C's map); scene change 2XX→3XX, A→B (small), A→C (large).
- Report room-scan coverage next to 4XX results.

## 5. Code and workflow

- **`scr_anchor.py`** (this repo): `train` and `eval`. It imports `rgbd-us/scr.py` and `dataloader.py` from `$RGBD_US` (default `../rgbd-us`), so network, labels, solver and frame selection are the rgbd-us ones. Checkpoints keep the `scr.py` format (`anchoring.py evaluate --anchor scr --scr-ckpt` takes them). Every `--check-every` epochs a **fit check** runs on 120 fixed training frames in eval mode, fp32, no augmentation: coordinate error per frame, the same after the best rigid fit, and the PnP pose of those frames.
- Old code (`dataset.py`, `model.py`, `train.py`, `eval.py`, `loss.py`, `solver.py`, `smoothing.py`, `geometry.py`) belongs to the earlier scr1–4 attempt (pooled data incl. 1XX, validated on a deleted collection); not used, not comparable. Its runs were removed.
- The user runs everything on the training PC and does all git push / pull; checkpoints (`*.pt`) are git-ignored.

```bash
export RGBD_US=/data2/u0137815/rgbd-us DATA=/data2/u0137815/rgbd-us/data
python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --out runs/s1-e120-2XX \
  --epochs 120 --check-every 6 --workers 16 --eval-root $DATA/train_2XX --eval-runs run-205 run-211
python scr_anchor.py eval --ckpt runs/s1-e120-2XX/best.pt --test-root $DATA/train_3XX
```

## 6. SCR model and training (current)

Model = `rgbd-us/scr.py` SCRNet, unchanged: RGB 360 × 640 → ImageNet EfficientNet-B0 to stride 16, stride-8 (40 ch) and upsampled stride-16 (112 ch) features concatenated → 1×1-conv head 152 → 256 → 256 → 256 → 3 (0.17 M parameters) → room coordinate per cell of a 45 × 80 grid (one per 16 × 16 full-resolution pixels). No depth input. Photometric augmentation only.

| | `scr.py` (baseline) | **S1** (`scr_anchor.py` defaults) |
|---|---|---|
| room-scan frames | every 2nd | all |
| loss | Huber on the 3D error, 50 mm knee | plain 3D distance |
| schedule | OneCycle, 15 epochs (2XX: 5,025 steps) | flat lr for 60 %, then cosine to 0; 30 epochs (20,100 steps) |
| head output | fp16 under autocast (~1–2 mm spacing at 1–2 m) | fp32 |
| lr | head 1e-3, encoder 1e-4, AdamW, batch 8 | same |

## 7. Results (21 Oct, map 2XX room scans → run-205, run-211)

| run | input | epochs (steps) | **anchor error mm, median / p90** | mean of sweep medians | rotation ° median / p90 | run-205 / run-211 | fit check: coordinates (after rigid) | pose of training frames | s / epoch |
|---|---|---|---|---|---|---|---|---|---|
| `s1-base-2XX` (scr.py recipe) | 360 × 640 | 15 (5,025) | 15.8 / 31.3 | 15.8 | 0.55 / 1.10 | 14.0 / 17.7 | 28.0 (26.7) mm | 13.2 mm | 18 |
| `s1-2XX` | 360 × 640 | 30 (20,100) | 6.3 / 13.1 | 6.3 | 0.34 / 0.55 | 6.5 / 6.0 | 14.5 (13.7) mm | 5.6 mm | 33 |
| `s1-e60-2XX` | 360 × 640 | 60 (40,200) | 5.3 / 11.3 | 5.4 | 0.26 / 0.47 | 4.9 / 6.0 | 13.0 (12.3) mm | 4.0 mm | 30 |
| **`s1-e120-2XX`** | 360 × 640 | 120 (80,400) | **5.1 / 11.3** | **5.1** | 0.31 / 0.53 | 5.3 / 4.9 | 11.5 (11.3) mm | 2.7 mm | 26 |
| `s3-full-2XX` | 720 × 1280 | 30 (20,100) | 7.1 / 14.5 | 7.3 | 0.33 / 0.55 | 6.6 / 7.9 | 15.7 (14.8) mm | 6.6 mm | 67 |
| classical anchors | | | 5.2 / 11.9 | 5.2 | 0.33 | 6.5 / 3.9 | | | |

All 100 % solved; 9–10 ms per frame (forward + RANSAC) at 360 × 640 on the training PC, 30 ms at full resolution. S0a: `scr_anchor.py eval` on the old `scr-3XX` checkpoint reproduces 9.8 / 22.1 mm exactly (`runs/s0a-scr-3XX`). Note: `runs/s1-2XX/history.json` was overwritten by a partial rerun (15 epochs, commit 22f576a); the full 30-epoch history is in commit c1bb9bb.

**Findings**
1. **The first SCR's gap came mostly from training, not from SCR.** Same network and data: 15.8 → 5.1 mm on 2XX validation. On this split SCR now matches classical anchors on the median (5.1 vs 5.2 mm) and p90 (11.3 vs 11.9), rotation alike; per sweep it is better on run-205 (5.3 vs 6.5) and worse on run-211 (4.9 vs 3.9).
2. **More steps have stopped paying on validation:** 30 → 60 epochs −1.0 mm, 60 → 120 −0.2 mm, while the training frames keep improving (pose 5.6 → 4.0 → 2.7 mm). The train/validation gap is opening, so the next gains must come from generalisation (viewpoint coverage, label consistency, augmentation) and capacity, not more steps.
3. **The residual error is scatter, not per-frame misalignment:** removing the best rigid fit hardly changes it (11.5 → 11.3 mm). RANSAC averages it, which is why ~12 mm coordinates give ~3–5 mm poses.
4. **Full resolution is not the lever now:** at the same steps it is worse (7.1 vs 6.3 mm) and 2× slower, despite 4× the inliers (9,573 vs 2,610) — the errors are correlated across neighbouring cells, so more cells do not average them out. Possibly also less context per cell (the receptive field is fixed in pixels).
5. One seed per setting: differences of ~1 mm on 77 frames may be noise; a seed repeat is needed before fine decisions.

## 8. Literature and diagnosis

| | Shotton '13 | DSAC* (RGB-D) | ACE | GLACE | ACE0 |
|---|---|---|---|---|---|
| model | forest, depth-normalised RGB-D features | FCN, stride 8, RGB input | frozen pretrained encoder (512-d, stride 8) + ~4 M-param 1×1 MLP head | ACE + global feature, feature-noise regulariser | ACE, mapping without poses, pose refinement |
| training | random pixels | whole images; 3D loss → reprojection → end-to-end | shuffled buffer of millions of pixel features, ~5 min | as ACE | incremental |
| depth | input + 3D–3D Kabsch | labels + Kabsch at test time, not an input | not used | not used | not used |

Causes of the first SCR's 24–28 mm (ranked): (1) optimisation budget — ~3,400 steps of correlated whole-image batches with the lr annealed to 0 while still falling (**confirmed** by S1); (2) head capacity — 0.17 M parameters vs ACE's ~4 M (open, S2); (3) Huber knee 50 mm shrinking the gradient below 5 cm (fixed in S1); (4) training error reported in train mode with augmentation (fit check added). Floors: fp16 output (fixed), label consistency (~5–6 mm per label, view-dependent hand-eye error; open, S0d).

Design questions: frozen ACE encoder + pixel buffer vs fine-tuned whole images — test at equal time (S2). Resolution — helps only once errors are independent (S3 says not yet). Depth — test-time Kabsch / refinement first (no retraining), then RGB-D input, then ICP against the room scan (hybrid, reported separately). Confidence — for RANSAC sampling only, not to down-weight the loss. Loss — D435i noise is along the ray, which PnP ignores: 3D loss for initialisation, then reprojection (DSAC*). Mapping data — all frames; ACE-style scale / in-plane rotation augmentation for low coverage (4XX); other sweeps only as a labelled extra.

**Honest outlook:** in an unchanged room, SCR alone matching 2.6 mm (3XX) is still unlikely because of the view-dependent label floor; 2XX validation says it is closer than expected. SCR is likely weakest at low coverage (4XX). Where it can win: no retrieval or pose prior (start pose, recovery), speed (~10 ms), re-mapping a room in minutes, possibly large changes if the receptive field stays local.

## 9. Plan and status

Pass criteria are against classical anchors on the same split. Settings chosen on 2XX validation only.

| step | what | status |
|---|---|---|
| S0a | evaluator reproduces scr.py | **done**: 9.8 / 22.1 mm exactly |
| S0b | oracle: true coordinates + synthetic independent / correlated error through the solver (run-316, this machine) | to do |
| S0c | fit check: eval-mode error, rigid vs residual | **done**, built into `train` |
| S0d | label-consistency floor in the room scans vs baseline / rotation; refine T_marker_cam if it grows with rotation | to do — now the most relevant check (finding 2) |
| S1 | optimisation fixes; pass: ≥ 30 % better than baseline, fit < 10 mm | anchors **pass** (−68 %); fit 11.5 mm at 120 epochs, not yet < 10 |
| S1-long | 60 / 120 epochs | **done**: 120 epochs best (5.1 mm), saturating |
| seed repeat | noise level of the val numbers | to do |
| v1 test | freeze `s1-e120` recipe; 3XX, 4XX A–E, scene change; then `anchoring.py --anchor scr` for the US-image error | to do |
| S2 | capacity: ACE-sized head; frozen ACE encoder with pixel buffer | to do (needs code) |
| S3 | resolution | 720 × 1280 tried early: worse at equal steps |
| S4 | depth at test time (Kabsch, PnP + depth refinement), RGB-D input, ICP hybrid | to do (needs code) |
| S5 | 3D → reprojection loss | to do |
| S6 | confidence for RANSAC sampling | to do |
| S7 | mapping data and coverage curve | to do |
| S8 | final protocol; competitive if ≤ 1.3× classical; A→C < 20 mm with ≥ 80 % solved | to do |

## 10. Literature
- Shotton et al., "Scene Coordinate Regression Forests for Camera Relocalization in RGB-D Images", CVPR 2013: https://openaccess.thecvf.com/content_cvpr_2013/html/Shotton_Scene_Coordinate_Regression_2013_CVPR_paper.html
- Brachmann & Rother, "Visual Camera Re-Localization from RGB and RGB-D Images Using DSAC" (DSAC*), TPAMI 2022: https://arxiv.org/abs/2002.12324
- Brachmann et al., "Accelerated Coordinate Encoding: Learning to Relocalize in Minutes using RGB and Poses" (ACE), CVPR 2023: https://arxiv.org/abs/2305.14059
- Wang et al., "GLACE: Global Local Accelerated Coordinate Encoding", CVPR 2024: https://openaccess.thecvf.com/content/CVPR2024/html/Wang_GLACE_Global_Local_Accelerated_Coordinate_Encoding_CVPR_2024_paper.html
- Brachmann et al., "Scene Coordinate Reconstruction" (ACE0), ECCV 2024: https://arxiv.org/abs/2404.14351
- Brachmann et al., "On the Limits of Pseudo Ground Truth in Visual Camera Re-localisation", ICCV 2021: https://openaccess.thecvf.com/content/ICCV2021/html/Brachmann_On_the_Limits_of_Pseudo_Ground_Truth_in_Visual_Camera_ICCV_2021_paper.html
- Sattler et al., "Understanding the Limitations of CNN-based Absolute Camera Pose Regression", CVPR 2019: https://arxiv.org/abs/1903.07504









