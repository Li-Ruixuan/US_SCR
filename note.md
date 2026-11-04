# US_SCR: working notes

Status 3 Nov 2026. Results: `summary.md`. Run index: `runs/README.md`. Setup and commands: `README.md`. Source project: `rgbd-us` (`note_RPR.md` there). The earlier, longer version of these notes (status tables, experiment log) is in git commit 870a144.

## 1. Objective, questions, claims (updated 3 Nov 2026)

**Objective.** The pose of every freehand US frame from a probe-mounted RGB-D camera (RealSense D435i) alone, **with no tracker at any stage**: none during the exam and none to prepare the room. A 1–2 min room scan becomes a room model by one SCR network that makes its own training labels (`scr_map.py`); during the exam the same kind of network gives the camera pose of every frame (`scr_anchor.py track`). Accuracy is a threshold, not the competition: good enough for 3D reconstruction (a few mm at the US image, ~16 cm from the camera, 1° ≈ 1.6 mm; volume shape ~2–3 mm). Sub-millimetre optical tracking exists; the point is a useful pose with nothing outside the probe and no prepared room.

**What still uses Polaris.** (1) The camera calibration, one camera-frame transform per probe, now fitted on a room scan (3XX); like the US calibration it is measured once per probe, in deployment with a phantom. (2) The evaluation: ground truth, and one rigid alignment per session to put the map in the Polaris frame. (3) Row selection in the code (rows with a marker pose), an engineering shortcut. Nothing per room and nothing per exam.

**Research questions and current answers**

| | question | answer so far | evidence |
|---|---|---|---|
| RQ1 | Can a probe-mounted RGB-D camera and one learned model track freehand US with no tracker at any stage? | **Yes:** 3XX 2.34 mm at the US image, shape 1.72 mm (strict protocol 2.94); 4XX shape 2.69 mm, best of all systems; every frame mapped and tracked. 2XX validation is the exception (8.06 mm, poor map) | Results without a tracker, below |
| RQ2 | What does removing the tracker cost? | 3XX about 0.5 mm (2.34 / 1.72 vs 1.85 / 1.57 with Polaris labels); 4XX nothing in shape (2.69 vs 3.17) but 1.4 mm in absolute placement (7.92 vs 6.48). The network reproduces its labels, so the map is the bottleneck, not the network | below |
| RQ3 | Learned room coordinates vs the alternatives? | vs pose regression 8× better on anchors (strong); vs a classical SIFT pipeline on the same Polaris-posed map: better where the scan covers the sweeps, worse where not, shape better everywhere | Tables A–D |
| RQ4 | What decides the accuracy? | room-scan coverage of the sweep viewpoints; for maps without a tracker also the map's slow bending (pose graph, loop closures) and the probe calibration | Table C, F |
| RQ5 | Do the US images help? | no (10 tests, Li et al. reproduced) | summary 6 |

**Claims.** The main claim is the tracker-free system; the earlier claims (summary 1.1, all with Polaris-posed maps) now describe its tracking part.

| | claim | evidence | strength | state with it |
|---|---|---|---|---|
| **C0** | **No tracker at any stage:** a 1–2 min room scan, one SCR network that labels itself, then every frame tracked | 3XX 2.34 / 1.72 mm (Polaris labels 1.85 / 1.57; classical with a Polaris-posed map 3.11 / 2.47); strict 2.94 (Polaris labels 2.98, classical 3.0); 4XX shape 2.69, best of all systems on every block | strong for shape, moderate for absolute | probe calibration fitted with Polaris once; 4XX absolute 7.92 vs 6.48 / 4.76; 2XX validation map failed (8.06 vs 3.35); one seed so far |
| C1 | One network on every frame replaces odometry + anchors | all 7 splits (Polaris maps) | strong | |
| C2 | Room coordinates + geometric solver beat pose regression | anchors 8× more accurate on 3XX and 4XX | strong | |
| C3 | Room-scan coverage decides the accuracy | covered 4.1 vs uncovered 13.4 mm; real views 4XX A 5.6 → 2.0 | strong | |
| C4 | SCR uses all room scans of the day despite moved objects; feature matching cannot | 4XX B–E 6.82 → 5.53 vs 4.90 → 13.93 | strong | pooling decided on test blocks |
| C5 | Smoother tracking and better volume shape than classical | every split | strong / moderate | shape metric introduced after the 4XX gap |
| C6 | The US images add nothing | 10 tests | strong (this setup) | |
| C7 | Real time | 0.25 s delay = offline | moderate | replayed, not live |

**Not claimed:** one network trained end to end (one SCR network + exact geometry: Kabsch, ICP, pose graph; deliberate, pose regression failed); as accurate as Polaris labels; better than classical in new sessions with short scans; generalisation to new rooms (trained per room by design); a fully Polaris-free workflow (the calibration).

**Gap in the evidence.** Every classical comparison uses a Polaris-posed map: the classical system's keyframe poses come from Polaris (`baselines/anchoring.py`). Only classical odometry is tracker-free (shape 6.23 vs our 1.72). A reviewer will ask "why not RGB-D SLAM?": the missing baseline is an off-the-shelf RGB-D SLAM (e.g. ORB-SLAM3 RGB-D) on the room scan + sweeps, scored after the same one alignment per session. A cheap internal step: the classical anchors on our own tracker-free map (same map, network vs SIFT).

**Results without a tracker (3 Nov; `runs/repro/`, `runs/map-*`, `runs/track-v2map-*`).** Parity: the cleaned code reproduces the old numbers exactly (`runs/parity/`: 1.85 / 1.57; classical 3.11 / 2.47).

| split | map: scene pts / camera / 1 s motion (mm) | US absolute (jitter) | shape | Polaris labels | classical |
|---|---|---|---|---|---|
| 3XX (repro, loops) | 2.6 / 2.0 / 1.5 | **2.34** (0.90) | **1.72** | 1.85 / 1.57 | 3.11 / 2.47 |
| 3XX same rows as classical | | 2.35 | 1.73 | | 3.11 / 2.47 |
| 3XX real time (1 s window, 0.25 s delay) / causal (0.25 s) | | 2.34 (0.90) / 2.42 (1.13) | | 1.86 / 1.95 | |
| 3XX strict (room-301 only, own calibration) | 2.6 / 2.2 / 1.9 | **2.94** (1.17) | | 2.98 (1.18) | 3.0 |
| 2XX validation (3XX calibration) | 6.7 / 8.3 / 3.6 (p90 31.2) | 8.06 (2.57) | | 3.35 (1.20) | 4.2 |
| 4XX A / B / C / D / E (own scans, 3XX calibration) | 3.1–3.9 / 3.0–4.8 / 1.4–2.4 | 5.04 / 6.55 / 9.40 / 11.54 / 7.07, mean **7.92** | 2.94 / 2.40 / 2.05 / 3.10 / 2.98, mean **2.69** | 6.48 / 3.17 | 4.76 / 3.34 |

- Loop closures: on the same 3XX map, scene points 4.5 → 2.6 mm, camera 5.2 → 2.0 mm, rotation 0.55° → 0.19° (`runs/repro/map-3XX-noloops`). Adopted (default).
- Probe calibration 31.7 mm, 1.51° (3XX); per scan 32.8 / 31.0 mm, 1.52° / 1.57° (each valid on the other scan); strict room-301 33.0 mm, 1.51°; 4XX scans 30–34 mm but 1.9–2.05°. No camera–Polaris timing offset (best +3 to +9 ms everywhere).
- 3D pages, 3XX (`runs/repro/volume3d/index.html`): mean pixel error over the compounded volumes 2.5 (no tracker) vs 3.2 (classical) vs 10.1 (odometry only); per sweep 3.0 / 2.5 / 2.5 / 1.9 / 2.8.
- 2XX validation fails: round 1 places 48 % of the frames, round 2 makes the map worse (camera 18.6 → 22.1 mm), the per-scan calibrations disagree (0.93° vs 1.89°) and the 1 s motion has a 31 mm p90, so some frames were joined wrongly and the pose graph did not fix them. 2XX has the longest scans (3 min, 5,366 frames). To investigate before the paper.
- Not run yet: seeds 1 and 2; 4XX with pooled scans; 3D pages for 4XX (`runs/volume3d-trackerfree/`); RGB-D SLAM baseline; C/D placement analysis.

**How the tests are organised (paper and webpage).** Main result: the tracker-free system (Table F). Every other test is one of:
- *Ablations of the mapping* (3XX, no tracker): frame-by-frame map → + pose graph → + camera calibration; prior 10 / 30 mm; joint refinement; loop closures; the oracle map (Polaris) as the upper bound.
- *Ablations of the tracking*, run with the oracle map so that only the tracker changes: training length, head and labels, pooled scans, scan length, augmentation, frozen encoder, rendered views; PnP vs Kabsch, inlier gate, refined fit, multi-frame anchors, confidence weighting; smoothing, real time, added odometry (SIFT, learned).
- *Comparisons with other methods*: pose regression (anchor network, RPRNet), classical SIFT system (Polaris-posed map), hybrid SCR + SIFT odometry, Li et al. (US only); missing: RGB-D SLAM.
- *Analyses*: coverage, where the error sits (shape vs placement), strict protocol, outdated maps, the ultrasound images (U1–U3, fusion).

**Role of Polaris in the recordings and the paper.** Recorded with every frame as the reference standard: ground truth for every error, one alignment per session for the absolute error, the one-off probe calibration, the oracle map of the ablations, and the map of the classical baseline. Never an input of the system.

**Metrics for a tracker-free system.** Absolute error after one rigid alignment per session (the map's frame is arbitrary; never per sweep), volume shape after a rigid fit per sweep, relative motion between nearby frames, jitter. Shape and relative motion need no alignment and are the fairest headline numbers.

**Status.** Tracking system: one SCR network (EfficientNet-B0 + big 1×1 head) on every frame → Kabsch RANSAC on the measured depth → temporal smoothing. It replaced the hybrid "SCR anchors every 1 s + SIFT odometry + pose graph" (`baselines/anchoring_kabsch.py`), which is no better (`summary.md` 3.1). Mapping without a tracker: seed by depth ICP, rounds of train / localise / extend, final pass, pose graph (depth-ICP edges, loop closures, network priors), camera calibration. Code layout (cleaned 3 Nov): root = the system (`scr_map.py`, `scr_anchor.py`, `scr.py`, `dataloader.py`, `geometry.py`); `tools/` = evaluation and figures; `baselines/` = classical / hybrid systems and the RPR stack; `studies/` = not adopted. README sections 4–7: the pipeline, the benchmark, the baselines, reproduction.

## 2. Workflow

- Code is edited on this machine; the user runs everything on the training PC and does all git push / pull. Give plain foreground `python ...` commands.
- This machine (RTX 3050, 4 GB, `~/anaconda3/envs/gpu/bin/python`): code only, no training or processing runs.
- Training PC (RTX A4500, 20 GB): data at `/data2/u0137815/rgbd-us/data/train_<NXX>/`; `test_4XXA` … `test_4XXE` are folders of links into `train_4XX`; rgbd-us at `/data2/u0137815/rgbd-us` (its `runs/` holds the odometry runs and anchor pairs the hybrid system needs).
- Checkpoints (`*.pt`, `saved_model/`) are git-ignored and live on the training PC.
- Every new setting gets a rule fixed before the run, decided on 2XX validation (run-205, run-211); tests only report.

```bash
export DATA=/data2/u0137815/rgbd-us/data
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/v2-3XX
python scr_anchor.py eval  --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX            # anchors, one frame per second
python scr_anchor.py track --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/track-3XX
```

`train`'s defaults are the final recipe (v2) since 2 Nov 2026; the v1 recipe is `--head small --label-max-depth 3000 --keep-depth-edges`.

Without a tracker (README 4; `train --map` takes the map's labels and `track` then applies its camera calibration):

```bash
python scr_map.py --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/map-3XX
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --map runs/map-3XX --out runs/v2map-3XX
python scr_anchor.py track --ckpt runs/v2map-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/track-v2map-3XX
python tools/us_analysis.py shape --json runs/track-v2map-3XX/poses/*.json --out runs/track-v2map-3XX/shape.md
```

The map without a tracker is the target approach (3 Nov). Open: reproduce Table F from scratch with the cleaned code (`runs/repro/`); loop closures (new default) vs none as the ablation; then 4XX with the 3XX camera calibration fixed (`scr_map.py --cam-calib-from runs/repro/map-3XX/map.json`): first each block's own scans (A: 401/402, B: 403/404, C: 405/406 for C, D, E; Polaris-label references 5.14, 5.77, 5.63, 9.63, 6.25 mm), then the pooled scans of the day.

## 3. Data

| collection | room scans | sweeps | role |
|---|---|---|---|
| 1XX (8 Oct) | room-101, 102 | run-101…112 | **do not use**: depth wrong, marker often lost |
| 2XX (9 Oct) | room-201, 202 (3.0 min, 5,366 frames) | run-201…212 | main session; **validation run-205, run-211** |
| 3XX (9 Oct) | room-301, 302 (2.0 min, 3,356 frames) | run-313…317 | clean test: same room as 2XX, a few small objects moved; room-301 recorded between run-314 and run-315, room-302 after all sweeps |
| 4XX A (14 Oct) | room-401 (90 s), 402 (40 s) | run-401…408 | new session |
| 4XX B | room-403, 404 (40 s each) | run-409…412 | small rearrangement |
| 4XX C | room-405, 406 (40 s each) | run-413…416 | large rearrangement |
| 4XX D | C's scans | run-418…421, 423, 424 | second subject |
| 4XX E | C's scans | run-425…428 | occlusion (arm in view) |

Per run: `frames.csv` (one row per RGB frame, ~30 Hz: `timestamp`; `rgb`, `depth`, `us` paths; `tx, ty, tz` mm and `qx, qy, qz, qw` scalar last = `T_world_marker`, clock offset already applied, **empty = marker lost**; `us_air` = 1 probe not on the skin; `us_repeat` = 1 same US frame as the row before), `rgb/` 1280 × 720, `depth/` aligned to RGB, uint16 mm, 0 = invalid, reliable 100–3000 mm, `camera_info.json` (fx ≈ 919.8, fy ≈ 919.5, cx ≈ 652.9, cy ≈ 373.6, no distortion), `us/` + `us_roi.json` (sweeps), `match_report.json`; ignore `depth_raw/`.

**Camera pose:** `T_world_cam = T_world_marker @ T_marker_cam`, world = Polaris frame (not moved between 2XX and 3XX). **`T_marker_cam.npy` must be the rgbd-us one** (mm, board-corner error 3.5 mm). **US image pose:** `T_world_cam @ inv(T_marker_cam) @ rigid @ scaling` with `calib_matrix.csv` (TUS-REC format, 1-based pixels on the US crop resized to 640 × 480, 0.2295 × 0.2213 mm/px).

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

**Sensor and labels:** D435i, 50 mm stereo baseline, depth noise ~ distance² (under ~2 % at 2 m), mostly along the ray. Room points re-projected across frames 1 s apart agree within 7.9 mm (median) at 1–1.5 m. The 3.5 mm hand-eye error makes labels view-dependent. Never train on hands/arms, the sleeve (4XX D/E) or the subject.

**Quirks:** `record_config.json` in 3XX carries old run names (run-316 says `run-216`), trust the folder name; in 4XX, run-427 was run-422 and run-428 was run-417.

## 4. Literature

| | Shotton '13 | DSAC* (RGB-D) | ACE | GLACE | ACE0 | KFNet |
|---|---|---|---|---|---|---|
| model | forest, RGB-D features | FCN, stride 8 | frozen encoder + ~4 M 1×1 head | ACE + global feature | ACE, mapping without poses | SCR + Kalman filter over video |
| depth | input + Kabsch | labels + Kabsch | not used | not used | not used | not used |
| relevance | depth at test time | our pose solver | head size, augmentation | generalisation | Polaris-free maps | our single-network tracking |

Pose regression (PoseNet, MapNet, VLocNet, our RPR) stays behind structure-based methods (Sattler et al., CVPR 2019); learned systems that work are hybrids of learned correspondences and geometric solvers. Learned inlier weights + weighted Kabsch: Deep Global Registration (Choy et al., CVPR 2020). Recon2Servo (arXiv 2610.06010): training pairs rendered from a reconstruction, a frozen foundation encoder with LoRA; the rendering idea is our open task for coverage. US-only: Li et al. (TBME 2024), reproduced and negative on our data (`summary.md` 6).









 




  

 

