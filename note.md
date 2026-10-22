# US_SCR: scene coordinate regression anchors for markerless US probe tracking

Status 22 Oct 2026. Source project: `rgbd-us` (`note_RPR.md` there has every detail of the earlier work).

## 1. Problem and goal

A probe-mounted RGB-D camera (Intel RealSense D435i, colour 1280 × 720) looks at the room; an NDI Polaris marker on the probe gives ground truth (~0.25 mm). The goal is the probe pose of every US frame with nothing outside the probe. Target: **~2 mm at the US image**, ~16 cm from the camera (1° of rotation ≈ 1.6 mm at the image bottom).

The system: **odometry** between frames + **anchors** (absolute poses against a room scan recorded before the exam), combined in an offline **pose graph**. Both are needed: odometry alone drifts; anchors alone jump from step to step; with good odometry an anchor every 1–2 s is enough. Best rgbd-us system: classical odometry + classical anchors (SIFT + PnP-RANSAC with depth), **3.3 mm at the US image on 3XX, 3.6–7.0 mm on 4XX**.

This project replaces the anchors with **scene coordinate regression (SCR)**: a network predicts the room coordinate of every image cell; a geometric solve turns those correspondences into a pose.

## 2. Current state

**Best SCR anchor: v1 + Kabsch** — the rgbd-us `scr.py` network trained with the S1 recipe for 120 epochs on the session's room scans (section 4), pose by 3D–3D RANSAC between the measured depth and the predicted room coordinates (`eval --solver kabsch`).

Anchor accuracy: camera position error against Polaris, one frame per second, **mean of per-sweep medians / p90 (mm)**, rotation median. SCR solves every frame (no gate yet); classical and the anchor network report the share of anchors their 50 mm gate accepted.

| split | **SCR v1 + Kabsch** | SCR v1 + PnP | classical anchors | RPR anchor network (adapted) | first SCR (`scr.py`) |
|---|---|---|---|---|---|
| 2XX val (settings chosen here) | **3.4 / 8.7, 0.33°** | 5.1 / 11.3 | 5.2 / 11.9, 0.33° | — | 15.8 / 31.3 |
| 3XX, clean test | **2.0 / 3.3, 0.19°** | 2.5 / 5.4 | 2.6 / 6.9, 0.34° | 15.3 / 27.5 (93 %) | 9.8 / 22.1 |
| 4XX A, new session | 5.9 / 10.1, 0.48° | 9.9 / 17.6 | **5.3 / 10.1, 0.48°** | 40.3 / 78.2 (73 %) | 17.7 |
| 4XX B, small change | 5.9 / 9.2, 0.40° | 8.6 / 17.8 | **3.2 / 5.0, 0.25°** | 25.4 / 51.5 (92 %) | 16.0 |
| 4XX C, large change | **5.2 / 10.1**, 0.74° | 11.2 / 17.0 | 5.9 / 11.1, 0.39° | 67.0 / 120.5 (66 %) | 21.8 |
| 4XX D, subject 2 (C's map) | 9.3 / 18.9, 0.73° | 15.4 / 29.2 | **7.1 / 18.3, 0.41°** (98 %) | 54.5 / 89.2 (58 %) | 26.0 |
| 4XX E, occlusion (C's map) | 5.9 / 13.9, 0.46° (99 %) | 10.2 / 20.5 | **5.2 / 8.5, 0.35°** | 57.9 / 124.6 (37 %) | 22.1 |
| outdated map 2XX → 3XX | **6.5 / 11.8, 0.44°** | 21.2 / 47.8 | 10.4 / 20.3, 0.55° | 39.8 / 71.1 (82 %) | — |
| outdated map A → B | 14.0 / 25.4, 0.56° | 31.7 / 47.3 | **7.9 / 12.9** (92 %) | 81.6 / 103.9 (50 %) | 50.3 |
| outdated map A → C | **13.4** / 113.0, 1.30° | 47.4 / 65.2 | 80.1 / 98.3 (21 %) | 51.8 / 108.8 (64 %) | 55.3 |

Time per frame on the training PC: PnP ~10 ms, Kabsch ~50–70 ms (numpy RANSAC). Run-to-run noise ~1 mm (seed repeat), so differences below ~1 mm are not meaningful. The comparison with classical is close but not identical: classical is evaluated at the odometry chain's anchor times (28 per sweep, vs 29 here) and retrieves keyframes near the odometry pose, i.e. it has a pose prior; SCR has none.

**In short**
- **Unchanged room, good coverage (3XX): SCR beats classical** (2.0 / 3.3 vs 2.6 / 6.9 mm, rotation 0.19 vs 0.34°) without keyframes or a pose prior.
- **New session with short room scans (4XX): on par on A, C, E; behind on B (5.9 vs 3.2) and D (9.3 vs 7.1); rotation worse throughout** (0.40–0.74 vs 0.25–0.48°).
- **Outdated maps:** better than classical on 2XX → 3XX and on the large change A → C (13.4 mm median at 100 % solved, where classical breaks), worse on A → B. A → C has a heavy tail (p90 113 mm) that an inlier gate removes (section 3, finding 7).
- **3–6× better than the RPR anchor network everywhere.**
- **At the US image** (table below): SCR + classical odometry is the best system on 3XX (2.1–2.6 vs 2.9–3.2 mm) and 2–3× better than the first SCR everywhere, but 1.3–1.7× worse than classical + classical on 4XX. The camera-position anchor error does not carry over one to one: on 4XX C the SCR anchors are better at the camera (5.2 vs 5.9 mm) but worse at the US image (6.4 vs 4.6 mm), because their rotation is worse (0.76 vs 0.39°; 1° ≈ 1.6 mm at the image).

**Full system: error at the US image** (`tools/anchoring_kabsch.py` = rgbd-us `anchoring.py` with SCR + Kabsch anchors, gate ≥ 400 inliers; classical odometry, an anchor every 1 s, pose graph with the rgbd-us settings: anchor σ 11 mm / 1°). Median error at the US image (mm), mean step-to-step error in brackets; mean over sweeps. Same pipeline, odometry and frames for every column.

| split | classical odometry only | + classical anchors | + first SCR anchors | **+ SCR v1 + Kabsch** (pose graph) | + SCR v1 + Kabsch (offline, no pose graph) |
|---|---|---|---|---|---|
| 2XX val | 36.9 (2.25) | **4.2** (2.28) | — | 4.4 (2.23) | 4.6 (2.39) |
| 3XX | 9.5 (1.18) | 3.2 (1.09) | 6.6 (1.23) | 2.6 (1.07) | **2.1** (1.15) |
| 4XX A | 15.2 (1.11) | **4.2** (1.13) | 16.3 (1.34) | 5.5 (1.11) | 5.8 (1.33) |
| 4XX B | 11.3 (1.41) | **3.4** (1.33) | 11.5 (1.61) | 5.7 (1.34) | 6.2 (1.50) |
| 4XX C | 8.9 (1.27) | **4.6** (1.19) | 14.5 (1.49) | 6.4 (1.18) | 6.5 (1.27) |
| 4XX D | 12.7 (1.32) | **6.3** (1.19) | 20.8 (1.52) | 10.2 (1.22) | 10.3 (1.43) |
| 4XX E | 13.0 (1.76) | **4.8** (1.57) | 14.5 (1.91) | 6.4 (1.65) | 6.2 (1.78) |

Classical anchors without the pose graph: 2XX 5.0, 3XX 2.9, A 5.1, B 3.1, C 5.5, D 7.0, E 4.9. Anchors per sweep with the gate: 27–37 on D and E (a few gated out), the full count elsewhere.

Pose-graph setting for SCR anchors, chosen on 2XX validation: anchor σ 11 mm / 1° → 4.4 (2.23), 5 mm / 0.5° → 4.4 (2.20), 3 mm / 0.3° → 4.5 (2.22) mm; no difference, so the rgbd-us default (11 mm / 1°) stays. 2XX validation is dominated by run-205, where the odometry alone drifts to 64 mm.

**3D pages** (`tools/volume_pages.py` → `runs/volume3d-3XX/`, `runs/volume3d-4XX/`, pose graph): mean pixel error over the compounded US images, the metric of rgbd-us's headline table (classical + classical: 3.3 mm on 3XX).

| sweep | **SCR (Kabsch) + classical odometry** | classical + classical | classical odometry only |
|---|---|---|---|
| run-313 | **2.6** | 3.9 | 12.2 |
| run-314 | **2.7** | 3.3 | 7.0 |
| run-315 | **2.2** | 3.0 | 9.4 |
| run-316 | 2.4 | 2.4 | 11.6 |
| run-317 | 4.2 | 4.1 | 10.3 |
| **3XX mean** | **2.8** | 3.3 | 10.1 |
| run-405 (A) | 6.1 | **4.0** | 7.2 |
| run-410 (B) | 4.9 | **3.6** | 11.5 |
| run-414 (C) | 9.1 | **4.4** | 10.7 |
| run-419 (D) | 10.1 | **7.0** | 11.9 |
| run-426 (E) | 6.3 | **3.6** | 13.5 |

On 3XX SCR is the best system in the headline metric (2.8 vs 3.3 mm). On 4XX classical stays 1.4–2× better; on run-426 (occlusion) SCR's 6.3 mm compares with 11.6 mm for the first SCR (note_RPR).

## 3. What we learned

1. **The first SCR's gap came from training, not from SCR.** Same network and data, 2XX validation 15.8 → 5.1 mm (PnP) by fixing the optimisation: all frames, 3D-distance loss instead of a 50 mm Huber knee, 4× and then 16× the steps with a flat-then-cosine schedule instead of OneCycle to zero, fp32 head output.
2. **More steps stopped paying after ~60 epochs on validation** (30 → 60 → 120 epochs: 6.3 → 5.3 → 5.1 mm) while the training frames kept improving (pose 5.6 → 4.0 → 2.7 mm): the limit is generalisation, not fitting.
3. **Coverage explains most of the 4XX gap** (`runs/coverage_error.md`): frames with a room-scan pose within 30 mm and 10° have 4.1 mm median error, the others 13.4 mm (PnP); in 4XX A the error grows from 8 to 14 mm as the nearest room-scan pose goes from < 30 to 60–100 mm. The 4XX room scans (40–90 s) cover 0–14 % of the sweep frames, 3XX's 93–96 %. SCR does not extrapolate to unseen viewpoints; SIFT copes better.
4. **Depth at test time (Kabsch) is the largest gain after the training fix:** −1.7 mm on 2XX validation (passes the pre-set > 1 mm rule), 20–55 % on every test split, and it rescues outdated maps (2XX → 3XX 21.2 → 6.5 mm, A → C 47.4 → 13.4 mm): PnP is fooled by the changed appearance, a 3D–3D fit on measured geometry much less.
5. **Viewpoint augmentation (ACE: zoom 0.67–1.5, ±15°) is not adopted.** With PnP it helped 4XX A (9.9 → 6.1 mm) but cost 1.5 mm on 2XX validation; with Kabsch the gain on 4XX A shrinks to noise (5.9 → 5.1 mm) and it costs 3.1 mm on 2XX validation and 2.0 mm on the low-coverage validation split (room-202 only: 16.2 vs 18.2 mm). It also loosens the fit on the room scans (2XX training-frame pose 2.7 → 6.3 mm): the 0.17 M-parameter head lacks the capacity. Revisit with a bigger head.
6. **Full resolution (720 × 1280) did not help** at equal steps (7.1 vs 6.3 mm, 2× slower) despite 4× the correspondences: neighbouring cells make correlated errors that do not average out.
7. **A Kabsch inlier gate is the obvious reject rule:** ≥ 400 inliers keeps 94–100 % of the frames on every unchanged-room split (100 % on 2XX validation, where the threshold must be set) and cuts A → C from 13.4 / 113.0 to 8.2 / 16.6 mm at 49 % kept. Not applied yet.
8. **The residual error is scatter, not per-frame misalignment** (removing the best rigid fit barely changes it): RANSAC averages it, which is why ~12 mm coordinates give 2–5 mm poses.
9. **The low-coverage validation split (2XX mapped on room-202 only) is a weak proxy:** errors are much larger than on 4XX (16 vs 6 mm with Kabsch) and do not grow with pose distance, i.e. room-202 alone sees a different part of the room. Distance to the nearest room-scan pose is a rough coverage measure; view overlap would be better.
10. **US measures the out-of-plane motion, not the in-plane one** (`tools/us_inplane.py`, `runs/us-*`, 2XX, 3XX, 4XX A, 4XX D). U1: a rigid in-plane registration of US frames k = 1, 3, 10 apart is *worse* than assuming no in-plane motion (e.g. 2XX k = 10: 1.91 vs 1.55 mm); the sweeps move mostly out of plane and the cross-section changes rather than shifts — dropped. U2: the correlation after in-plane alignment falls with the out-of-plane distance along the same curve in every collection and both subjects (ncc 0.995 below 0.5 mm, 0.967 at 2–4 mm, 0.91–0.92 beyond 8 mm; Spearman −0.83 to −0.85). A curve built on 2XX predicts the out-of-plane distance on 3XX / 4XX A / 4XX D with 0.43 / 0.28 / 0.27 mm median error (p90 1.8–2.6), about half the error of predicting the median distance; at k = 10 (3–4.5 mm true) 0.9–1.3 mm. US gives the magnitude only; the sign comes from the camera.

## 4. Model, training, evaluation

Network = `rgbd-us/scr.py` SCRNet, unchanged: RGB 360 × 640 → ImageNet EfficientNet-B0 to stride 16; stride-8 (40 ch) and upsampled stride-16 (112 ch) features concatenated → 1×1-conv head 152 → 256 → 256 → 256 → 3 (0.17 M parameters) → room coordinate per cell of a 45 × 80 grid (one per 16 × 16 full-resolution pixels). No depth input.

| | `scr.py` (first SCR) | **current** (`scr_anchor.py train` defaults + `--epochs 120`) |
|---|---|---|
| training data | session room scans, every 2nd frame | session room scans, all frames |
| targets | room-scan depth at each cell centre, back-projected with the Polaris pose | same |
| loss | Huber on the 3D error, 50 mm knee | 3D distance |
| schedule | OneCycle, 15 epochs | flat lr for 60 %, then cosine to 0; 120 epochs |
| head output | fp16 under autocast | fp32 |
| augmentation | photometric | photometric (viewpoint augmentation available: `--aug-scale`, `--aug-rot`, off) |
| optimiser | AdamW, head lr 1e-3, encoder lr 1e-4, batch 8 | same |
| pose | PnP-RANSAC 10 px, ≥ 30 inliers | **Kabsch: 3D–3D RANSAC, 20 mm, cells < 2 m, ≥ 30 inliers** (`--solver kabsch`); PnP still the default |

**Test protocol** (identical to `rgbd-us/scr.py eval`): map on a session's **room scans only**; test on its sweeps, **one frame every 30 usable rows** (Polaris pose, not in the air, US frame and full-size depth present); report position (mm) and rotation (°) median and p90 and the share solved (`scr_anchor.py` adds the mean of per-sweep medians, inliers and ms, with a fixed RANSAC seed per frame). **Settings are chosen on 2XX validation only** (room-201/202 → run-205, run-211); 3XX and 4XX only report. Splits: 3XX → 3XX; 4XX A–E on their own scans (D, E use C's); outdated maps 2XX → 3XX, A → B, A → C.

## 5. Code and workflow

- **`scr_anchor.py`**: `train` and `eval`. Imports `rgbd-us/scr.py` and `dataloader.py` from `$RGBD_US` (default `../rgbd-us`), so network, labels and frame selection are the rgbd-us ones; checkpoints keep the `scr.py` format (`anchoring.py evaluate --anchor scr --scr-ckpt` takes them, PnP only for now). Every `--check-every` epochs a **fit check** on 120 fixed training frames (eval mode, no augmentation): coordinate error, the same after the best rigid fit, PnP pose of those frames.
- **`tools/coverage_error.py`**: anchor error against the distance to the nearest room-scan pose, per eval file.
- **`tools/draw_scr_anchor_diagram.py`** → `tools/scr_anchor_diagram.png/.pdf`: block diagram (its results box still shows PnP numbers).
- Old code (`dataset.py`, `model.py`, `train.py`, `eval.py`, `loss.py`, `solver.py`, `smoothing.py`, `geometry.py`) is the earlier scr1–4 attempt (pooled data incl. 1XX); not used, not comparable.
- The user runs everything on the training PC and does all git push / pull; checkpoints (`*.pt`) are git-ignored.

```bash
export RGBD_US=/data2/u0137815/rgbd-us DATA=/data2/u0137815/rgbd-us/data
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/v1-3XX \
  --epochs 120 --check-every 6 --workers 16 --eval-root $DATA/train_3XX
python scr_anchor.py eval --ckpt runs/v1-3XX/best.pt --test-root $DATA/train_3XX --solver kabsch
python tools/coverage_error.py runs/v1-*/eval_*/scr_eval.json
```

## 6. Data

- Training PC (RTX A4500, 20 GB): `/data2/u0137815/rgbd-us/data/train_<NXX>/`, all collections matched; rgbd-us at `/data2/u0137815/rgbd-us`; `data/test_4XXA` … `test_4XXE` are folders of links into `train_4XX`.
- This machine (RTX 3050, 4 GB): only `~/Desktop/rgbd-us/data/train_3XX/run-316` is matched; use `~/anaconda3/envs/gpu/bin/python`.

| collection | room scans | sweeps | role |
|---|---|---|---|
| 1XX (8 Oct) | room-101, 102 | run-101…112 | **do not use**: depth wrong, marker often lost |
| 2XX (9 Oct) | room-201, 202 (3.0 min, 5,366 frames) | run-201…212 | main session; **validation run-205, run-211** |
| 3XX (9 Oct) | room-301, 302 (2.0 min, 3,356 frames) | run-313…317 | **clean test**: same room as 2XX, a few small objects moved |
| 4XX A (14 Oct) | room-401 (90 s), 402 (40 s) | run-401…408 | new session |
| 4XX B | room-403, 404 (40 s each) | run-409…412 | small rearrangement |
| 4XX C | room-405, 406 (40 s each) | run-413…416 | large rearrangement |
| 4XX D | C's scans | run-418…421, 423, 424 | second subject |
| 4XX E | C's scans | run-425…428 | occlusion (arm in view) |

Per run: `frames.csv` (one row per RGB frame, ~30 Hz: `timestamp`; `rgb`, `depth`, `us` paths; `tx, ty, tz` mm and `qx, qy, qz, qw` scalar last = `T_world_marker`, clock offset already applied, **empty = marker lost**; `us_air` = 1 probe not on the skin; `us_repeat`), `rgb/` 1280 × 720, `depth/` aligned to RGB, uint16 mm, 0 = invalid, reliable 100–3000 mm, `camera_info.json` (fx ≈ 919.8, fy ≈ 919.5, cx ≈ 652.9, cy ≈ 373.6, no distortion), `us/` + `us_roi.json` (sweeps), `match_report.json`; ignore `depth_raw/`.

**Camera pose:** `T_world_cam = T_world_marker @ T_marker_cam`, world = Polaris frame (not moved between 2XX and 3XX). **`T_marker_cam.npy` must be the rgbd-us one** (mm, board-corner error 3.5 mm; this repo's old copy was 17.7 mm / 3.6° off and was replaced).

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
scene_coords = (T_wc @ X)[:3].T                                       # room coordinate (mm) of pixel (u, v)
```

**Sensor and labels:** D435i, 50 mm stereo baseline, depth noise ~ distance² (under ~2 % at 2 m), mostly along the ray. Room points re-projected across frames 1 s apart agree within 7.9 mm (median) at 1–1.5 m, ~5–6 mm per label. The 3.5 mm hand-eye error makes labels view-dependent; classical anchors cancel this by chaining off a keyframe ~30 mm away, a global SCR map has to average it. Not applied yet: down-weight far pixels or cap at ~2 m; drop depth edges; never train on hands/arms, the sleeve (4XX D/E) or the subject.

**Quirks:** `record_config.json` in 3XX carries old run names (run-316 says `run-216`), trust the folder name; in 4XX, run-427 was run-422 and run-428 was run-417.

## 7. Experiment log (`runs/`)

All 2XX runs map room-201/202 and test run-205/211; numbers are mean of per-sweep medians / p90 (mm), PnP unless marked.

| run | what | result |
|---|---|---|
| `s0a-scr-3XX` | evaluator check: old `scr-3XX` checkpoint | 9.8 / 22.1 on 3XX, reproduces `scr.py` exactly |
| `s1-base-2XX` | `scr.py` recipe | 15.8 / 31.3; fit 28.0 mm |
| `s1-2XX` | S1 recipe, 30 epochs | 6.3 / 13.1; fit 14.5 mm (its `history.json` was overwritten by a partial rerun; full one in commit c1bb9bb) |
| `s1-e60-2XX`, `s1-e60-seed1-2XX` | 60 epochs, seeds 0 and 1 | 5.4 / 11.3 and 6.3 / 12.9: noise ~1 mm |
| `s1-e120-2XX` | 120 epochs (**v1 recipe**) | 5.1 / 11.3; **Kabsch 3.4 / 8.7**; fit 11.5 mm, training-frame pose 2.7 mm |
| `s3-full-2XX` | 720 × 1280, 30 epochs | 7.3 / 14.5 |
| `v1-3XX`, `v1-4XXA/B/C` | v1 recipe on the test splits | section 2; fit on the room scans 4.0–6.9 mm, training-frame pose 1.2–1.7 mm |
| `aug-2XX`, `aug-4XXA` | v1 + viewpoint augmentation | 2XX 6.6 (Kabsch 6.5); 4XX A 6.1 (Kabsch 5.1) |
| `v1-short-2XX`, `aug-short-2XX` | low-coverage validation: room-202 only (60 s, 0 % covered) | PnP 40.2 vs 23.2; Kabsch 16.2 vs 18.2 |
| `coverage_error.md`, `coverage_short.md` | `tools/coverage_error.py` | section 3, findings 3 and 9 |

## 8. Literature and diagnosis

| | Shotton '13 | DSAC* (RGB-D) | ACE | GLACE | ACE0 |
|---|---|---|---|---|---|
| model | forest, depth-normalised RGB-D features | FCN, stride 8, RGB input | frozen pretrained encoder (512-d, stride 8) + ~4 M-param 1×1 MLP head | ACE + global feature, feature-noise regulariser | ACE, mapping without poses, pose refinement |
| training | random pixels | whole images; 3D loss → reprojection → end-to-end | shuffled buffer of millions of pixel features, ~5 min | as ACE | incremental |
| depth | input + 3D–3D Kabsch | labels + Kabsch at test time | not used | not used | not used |

Our results line up with this: Kabsch with depth at test time (Shotton, DSAC* RGB-D) was the biggest gain after the training fix; ACE's two other ingredients — a much larger head and viewpoint augmentation — are the next things to combine (augmentation alone did not pay with our small head).

## 9. Next steps

| priority | step | why | needs |
|---|---|---|---|
| 1 | **Error at the US image**: SCR + Kabsch anchors with classical odometry in `anchoring.py`, with an inlier gate (≥ 400, set on 2XX validation) | the headline number, comparable with rgbd-us's 3.3 mm (3XX) / 3.6–7.0 mm (4XX) | Kabsch + gate option in `anchoring.py` (rgbd-us) |
| 2 | **Bigger head (S2)**: ACE-sized 1×1 MLP (~4 M parameters), then with viewpoint augmentation again | capacity for unseen viewpoints (4XX B, D), finding 5 | code |
| 3 | **Rotation on 4XX** (0.40–0.74 vs classical 0.25–0.48°): weight cells by 1/z², or a final joint refinement of reprojection + depth residuals on the Kabsch inliers | 0.3° ≈ 0.5 mm at the US image | code |
| 4 | Label consistency / hand-eye check (S0d): multi-view disagreement of room-scan points vs viewing angle; refine `T_marker_cam` if it grows with rotation | the label floor for every method | script |
| 5 | Room-scan protocol for new recordings: record until `check_coverage.py` reports most sweep viewpoints covered | coverage is the largest error source (finding 3) | recording |
| 6 | **US out-of-plane factor (U3)**: add the speckle-decorrelation distance between US frames k apart (magnitude from US, sign from the camera; curve calibrated once on 2XX) as a partial factor in the offline pose graph, on top of the SCR-anchored camera trajectory; judge by the error and the step-to-step error at the US image. U1 (in-plane registration) dropped, U2 passed (finding 10). Reference for US-only: Li et al., "Long-term dependency for 3D reconstruction of freehand ultrasound without external tracker" (IEEE TBME 2024; the TUS-REC baseline), no better than zero motion in a new session in rgbd-us — so US refines the camera instead of replacing it | the out-of-plane spacing of the frames is what US measures to ~0.3 mm; the camera system's step-to-step error at the US image is ~1.1–1.7 mm | after step 1 (needs the SCR-anchored trajectories); code |
| later | RGB-D input, reprojection loss, frozen ACE encoder with a pixel buffer, faster Kabsch (GPU) | smaller or uncertain gains | code |


 
 
 
  
 










2. On the training PC: the seed repeat, two trainings in separate terminals, about 1 h each.


cd <your US_SCR clone> && git pull
export RGBD_US=/data2/u0137815/rgbd-us DATA=/data2/u0137815/rgbd-us/data

# terminal 1: v1, seed 1
python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --out runs/s1-e120-seed1-2XX \
  --epochs 120 --check-every 6 --workers 12 --seed 1 --eval-root $DATA/train_2XX --eval-runs run-205 run-211

# terminal 2: big head + clean labels, seed 1
python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --out runs/bigclean-seed1-2XX \
  --head big --label-max-depth 2000 --drop-depth-edges --epochs 120 --check-every 6 --workers 12 --seed 1 \
  --eval-root $DATA/train_2XX --eval-runs run-205 run-211
3. When both have finished: the Kabsch evals, a few minutes each.


python scr_anchor.py eval --ckpt runs/s1-e120-seed1-2XX/best.pt --test-root $DATA/train_2XX --test-runs run-205 run-211 --solver kabsch
python scr_anchor.py eval --ckpt runs/bigclean-seed1-2XX/best.pt --test-root $DATA/train_2XX --test-runs run-205 run-211 --solver kabsch
4. Push runs/ and tell me. Big head + clean labels gets adopted if, with both seeds, its rotation and p90 on 2XX are lower than v1's.