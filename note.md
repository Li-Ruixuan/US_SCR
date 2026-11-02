# US_SCR: working notes

Status 3 Nov 2026. Results: `summary.md`. Run index: `runs/README.md`. Setup and commands: `README.md`. Source project: `rgbd-us` (`note_RPR.md` there). The earlier, longer version of these notes (status tables, experiment log) is in git commit 870a144.

## 1. Goal and current system

A probe-mounted RGB-D camera (RealSense D435i) looks at the room; the pose of every US frame must come from it alone, ~2 mm at the US image (~16 cm from the camera; 1° ≈ 1.6 mm). Polaris (marker on the probe) is ground truth only.

**Current system:** one SCR network (EfficientNet-B0 + big 1×1 head, trained per room on its room scan) on every frame → Kabsch RANSAC on the measured depth → temporal smoothing (`scr_anchor.py track`). It replaced the hybrid "SCR anchors every 1 s + SIFT odometry + pose graph" (`baselines/anchoring_kabsch.py`), which is no better (`summary.md` 3.1).

**Without a tracker (3 Nov):** the room-scan poses that label the training come from the network itself (`scr_map.py`: seed by depth ICP, rounds of train / localise / extend, final pass, pose graph with depth-ICP edges and loop closures, camera calibration). 3XX: 3.60 mm at the US image, shape 2.86 (Polaris labels 1.85 / 1.57, classical 3.11 / 2.47), accepted as good enough (`summary.md` Table F). Polaris enters only the camera calibration (one camera-frame transform per probe, fitted on the room scan) and the evaluation.

**Code layout (cleaned 3 Nov):** root = the system (`scr_map.py`, `scr_anchor.py`, `scr.py`, `dataloader.py`, `geometry.py`); `tools/` = evaluation and figures; `baselines/` = classical / hybrid systems and the RPR stack; `studies/` = not adopted (`scr_render.py`, `li_baseline.py`). README sections 4–7: the pipeline, the benchmark, the baselines, reproduction.

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















git pull
export DATA=/data2/u0137815/rgbd-us/data ODO=/data2/u0137815/rgbd-us/runs

python scr_anchor.py track --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/parity/track-3XX

python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 --root $DATA/train_3XX --scan-runs room-301 room-302 --test-root $DATA/train_3XX --odometry-source classical-vo-train_3XX --odometry $ODO/rpr-rgb-gap8-12XX-gru8 --pairs $ODO/anchor-pairs/pairs_3XX.json --pgo --start anchor --out runs/parity/sys-classical-r-3XX

python tools/volume_pages.py --test-root $DATA/train_3XX --track runs/parity/track-3XX --anchoring runs/parity/sys-classical-r-3XX/anchor_eval_classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-train_3XX.json --extra classical-vo-train_3XX --labels "classical anchors + classical odometry" "classical odometry only" --out runs/parity/volume3d/3XX

python tools/us_analysis.py shape --json runs/parity/volume3d/3XX/poses/*.json --out runs/parity/shape-3XX.md
Expected: track gives 1.85 at 2 s smoothing, the classical system gives the same table as runs/sys-classical-r-3XX, and the shape file gives 1.85 / 1.57, 3.11 / 2.47 and 9.43 / 6.23.

Then the reproduction from scratch:


python scr_map.py --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/repro/map-3XX

python scr_map.py --root $DATA/train_3XX --scan-runs room-301 room-302 --from runs/repro/map-3XX --loop-k 0 --out runs/repro/map-3XX-noloops

python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --map runs/repro/map-3XX --out runs/repro/v2map-3XX

python scr_anchor.py track --ckpt runs/repro/v2map-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/repro/track-v2map-3XX

python tools/us_analysis.py shape --json runs/repro/track-v2map-3XX/poses/*.json --out runs/repro/shape-3XX.md

python tools/volume_pages.py --test-root $DATA/train_3XX --track runs/repro/track-v2map-3XX --out runs/repro/pages/3XX

git add -A && git commit -m "Parity check and from-scratch reproduction of the map without a tracker (3XX)" && git push
 





export DATA=/data2/u0137815/rgbd-us/data

python scr_map.py --root $DATA/test_4XXA --scan-runs room-401 room-402 --cam-calib-from runs/repro/map-3XX/map.json --out runs/map-4XXA
python scr_map.py --root $DATA/test_4XXB --scan-runs room-403 room-404 --cam-calib-from runs/repro/map-3XX/map.json --out runs/map-4XXB
python scr_map.py --root $DATA/test_4XXC --scan-runs room-405 room-406 --cam-calib-from runs/repro/map-3XX/map.json --out runs/map-4XXC

python scr_anchor.py train --root $DATA/test_4XXA --scan-runs room-401 room-402 --map runs/map-4XXA --out runs/v2map-4XXA
python scr_anchor.py train --root $DATA/test_4XXB --scan-runs room-403 room-404 --map runs/map-4XXB --out runs/v2map-4XXB
python scr_anchor.py train --root $DATA/test_4XXC --scan-runs room-405 room-406 --map runs/map-4XXC --out runs/v2map-4XXC

python scr_anchor.py track --ckpt runs/v2map-4XXA/best.pt --test-root $DATA/test_4XXA --every 2 --out runs/track-v2map-4XXA
python scr_anchor.py track --ckpt runs/v2map-4XXB/best.pt --test-root $DATA/test_4XXB --every 2 --out runs/track-v2map-4XXB
python scr_anchor.py track --ckpt runs/v2map-4XXC/best.pt --test-root $DATA/test_4XXC --every 2 --out runs/track-v2map-4XXC
python scr_anchor.py track --ckpt runs/v2map-4XXC/best.pt --test-root $DATA/test_4XXD --every 2 --out runs/track-v2map-4XXD
python scr_anchor.py track --ckpt runs/v2map-4XXC/best.pt --test-root $DATA/test_4XXE --every 2 --out runs/track-v2map-4XXE

python tools/us_analysis.py shape --json runs/track-v2map-4XX*/poses/*.json --out runs/shape-v2map-4XX.md

git add -A && git commit -m "Map without a tracker on 4XX (own scans, 3XX camera calibration)" && git push
