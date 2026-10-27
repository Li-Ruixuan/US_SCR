# US_SCR

Markerless pose estimation of a freehand ultrasound probe from a probe-mounted RGB-D camera, with **scene coordinate regression (SCR) anchors**: a network trained on a room scan predicts the room coordinate of every image cell, and a 3D–3D RANSAC (Kabsch) on the measured depth turns them into the camera pose. Results and discussion: `summary.md`; working notes and data guide: `note.md`.

## Problem and claim

Freehand 3D ultrasound needs the 6-DoF pose of every B-mode frame. External optical or EM trackers are accurate but expensive, line-of-sight constrained, and tie the exam to a prepared room. US-only sensorless estimation drifts far beyond the sub-millimetre budget set by the elevational beam width.

Given `{I_t_rgb, D_t, I_t_US}`, output `T_t ∈ SE(3)` in a room-fixed frame established at the start of the exam, from a single probe-mounted RGB-D camera — no markers, no fiducial pattern, no external infrastructure. Downstream: 3D volume reconstruction, and navigation relative to previously scanned anatomy.

**The goal is not a more accurate tracking system.** Sub-millimetre freehand US tracking already exists (optical ~0.5 mm, MLRecon 0.88 mm); beating it is neither likely nor interesting. The goal is a *useful* pose estimate with nothing outside the probe. Accuracy is a threshold to clear, not the axis of competition: miss it and the result is useless, clear it and the infrastructure argument becomes available. The claim is "this works without a prepared room", and the experiments should be built to support that, not a millimetre table.

## What runs from this repo alone

| | needs |
|---|---|
| train an SCR model, evaluate its anchors (`scr_anchor.py`) | this repo + the data |
| coverage analysis, US diagnostics (`tools/coverage_error.py`, `tools/us_inplane.py`) | this repo + the data |
| full system: odometry + anchors + pose graph, error at the US image (`tools/anchoring_kabsch.py`); 3D pages (`tools/volume_pages.py`) | this repo + the data + two rgbd-us **result folders** (no rgbd-us code): the odometry run (`runs/rpr-rgb-gap8-*-gru8`, its checkpoint and odometry caches in `preds/`) and the anchor pairs (`runs/anchor-pairs/`) |

All code is in this repo. The modules from rgbd-us (`dataloader.py`, `geometry.py`, `scr.py`, `anchoring.py`, `eval.py`, `poses.py`, `trajectory.py`, `model.py`, `loss.py`, `train.py`, `tools/anchor_classical.py`, `tools/anchor_saliency.py`, `tools/volume_3d.py`) are copies of rgbd-us commit a5bf2ce; only `anchoring.py` was changed here (options `--gate-recover`, `--scr-frames`).

## 1. Setup

```bash
git clone git@github.com:Li-Ruixuan/US_SCR.git && cd US_SCR
conda create -n usscr python=3.11 -y && conda activate usscr
# install torch + torchvision for your CUDA version from https://pytorch.org, then
pip install -r requirements.txt
```

A CUDA GPU is needed for training (we used an RTX A4500, 20 GB; a 4 GB GPU works for the quick check with `--batch-size 2`). The first run downloads the ImageNet weights of EfficientNet-B0 (internet needed once).

## 2. Data

One folder per collection, with room scans (`room-*`, mapping data) and sweeps (`run-*`, test data):

```
$DATA/train_3XX/
  room-301/  room-302/          room scans (no US)
  run-313/ … run-317/           sweeps
```

Each run folder needs:

| file | content |
|---|---|
| `frames.csv` | one row per RGB frame: `timestamp`, `rgb`, `depth`, `us` (paths), `tx, ty, tz` (mm), `qx, qy, qz, qw` (scalar last) = Polaris pose of the probe marker (empty = marker lost), `us_air`, `us_repeat` |
| `rgb/`, `depth/` | colour PNG 1280 × 720; depth aligned to colour, uint16, mm, 0 = invalid |
| `camera_info.json` | colour intrinsics `K`, `width`, `height`, `depth_scale` |
| `record_config.json` | must contain `{"pose": {"units": "mm"}}` |
| `us/`, `us_roi.json` | sweeps only: US screen grabs and the crop of the US image |

The hand–eye calibration (`T_marker_cam.npy`, marker → camera, mm) and the US calibration (`calib_matrix.csv`, TUS-REC format) are in the repo root; they are valid for all recordings with this probe and mount. Do not use the 1XX collection (broken depth). See `note.md` section 6 for the sessions.

## 3. Quick check (a few minutes, any GPU)

```bash
export DATA=/path/to/data
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 --out runs/quickcheck \
  --epochs 3 --max-frames 200 --batch-size 2 --workers 2 --check-every 3 --check-frames 10 \
  --eval-root $DATA/train_3XX --eval-runs run-316
```

It should print the frames found, one line per epoch, and an evaluation table (errors of several cm: three epochs on 200 frames only test the pipeline).

## 4. Train and evaluate

Train on a collection's room scans (defaults are the final recipe: 120 epochs, about 25–50 min on an A4500), then evaluate on its sweeps, one frame per second:

```bash
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/v1-3XX --eval-root $DATA/train_3XX
python scr_anchor.py eval --ckpt runs/v1-3XX/best.pt --test-root $DATA/train_3XX                 # Kabsch (default)
python scr_anchor.py eval --ckpt runs/v1-3XX/best.pt --test-root $DATA/train_3XX --solver pnp    # PnP, without depth
```

Outputs in `runs/v1-3XX/`: `config.json` (all settings), `history.json` (loss and fit check per epoch), `best.pt` (the model after the last epoch), and per evaluation `eval_<test>[_kabsch]/scr_eval.md` (table per sweep: position / rotation error against Polaris, median and p90, inliers, ms per frame) and `scr_eval.json` (every frame).

Options of `train`: `--head big` (larger head), `--label-max-depth 2000 --drop-depth-edges` (cleaner labels), `--aug-scale 0.67 1.5 --aug-rot 15` (viewpoint augmentation), and map extension: add sweeps to `--scan-runs` (labelled with their Polaris poses) or label them with the system's own estimate via `--label-poses <poses.py JSON>`. `python scr_anchor.py train -h` lists everything.

Coverage analysis of an evaluation:

```bash
python tools/coverage_error.py runs/v1-3XX/eval_train_3XX_kabsch/scr_eval.json --out runs/coverage_3XX.md
```

## 5. Full system (odometry + anchors + pose graph)

Needs the odometry run and the anchor pairs, result folders of rgbd-us (`runs/rpr-rgb-gap8-12XX-gru8` for 2XX/3XX, `runs/rpr-rgb-gap8-123XX-gru8` for 4XX, with the classical odometry caches in `preds/`; `runs/anchor-pairs/`). Set `ODO` to the folder that holds them and run from this repo's folder (anchoring writes its trajectories into `$ODO/<odometry run>/preds/`):

```bash
export DATA=/path/to/data ODO=/path/to/rgbd-us/runs
python tools/anchoring_kabsch.py -- evaluate --anchor scr --scr-ckpt runs/v1-3XX/best.pt \
  --root $DATA/train_3XX --scan-runs room-301 room-302 --test-root $DATA/train_3XX \
  --odometry-source classical-vo-train_3XX --odometry $ODO/rpr-rgb-gap8-12XX-gru8 --pairs $ODO/anchor-pairs/pairs_3XX.json \
  --pgo --start anchor --out runs/sys-final-3XX
python tools/volume_pages.py --test-root $DATA/train_3XX \
  --anchoring runs/sys-final-3XX/anchor_eval_scr-v1-3XX-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX.json \
  --extra classical-vo-train_3XX --out runs/volume3d-final/3XX
```

Classical anchors for comparison: `python anchoring.py evaluate --anchor classical` with the same data options. Options: `--start anchor` (no ground-truth pose at the start of a segment), `--gate-recover 3` (accept anchors again after a wrong one was accepted), `--scr-frames M` (one SCR anchor from M chain frames).

## Files

| file | purpose |
|---|---|
| `scr_anchor.py` | `train` and `eval` |
| `dataloader.py`, `geometry.py`, `scr.py` | data loading, geometry, SCR network (from rgbd-us) |
| `anchoring.py`, `eval.py`, `poses.py`, `trajectory.py`, `model.py`, `loss.py`, `train.py` | full system: anchors + odometry + pose graph, pose export, evaluation (from rgbd-us; `anchoring.py` extended here) |
| `tools/anchoring_kabsch.py` | full system with SCR + Kabsch anchors |
| `tools/volume_pages.py`, `tools/volume_3d.py` | interactive 3D pages of compounded sweeps |
| `tools/anchor_classical.py`, `tools/anchor_saliency.py` | classical (SIFT) anchors, used by `anchoring.py` (from rgbd-us) |
| `tools/coverage_error.py` | anchor error vs distance to the nearest room-scan pose |
| `tools/us_inplane.py` | US diagnostics: in-plane registration and speckle decorrelation |
| `tools/us_speckle.py` | US diagnostic U3: per-patch speckle decorrelation (out-of-plane shift + tilts) against Polaris and the pose system |
| `tools/shape_error.py` | shape of the reconstruction: error after a rigid fit of each sweep, relative error between nearby frames |
| `tools/li_repro.py` | reproduction of Li et al. (TBME 2024) with the authors' code (github.com/ucl-candi/freehand) and data (Zenodo 7740734): training with a fixed split, and the paper's metrics |
| `tools/li_transfer.py` | the Li et al. network on our sweeps: zero-shot, fine-tuned on our 2XX, or from scratch; paper metrics and relative motion against the camera system |
| `tools/draw_scr_anchor_diagram.py` | block diagram (`tools/scr_anchor_diagram.pdf/.png`) |
| `T_marker_cam.npy`, `calib_matrix.csv` | hand–eye and US calibration |
| `summary.md`, `note.md` | results; working notes and data guide |
| `runs/` | results (`*.pt` checkpoints are not in git) |

Runs made before 23 Oct 2026 used options removed in the clean-up (the first SCR's Huber loss and one-cycle schedule, Kabsch refinement); their `config.json` records the settings and commit `3599239` has the code that produced them.
