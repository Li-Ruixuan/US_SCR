# US_SCR

Markerless pose estimation of a freehand ultrasound probe from a probe-mounted RGB-D camera with **one scene coordinate regression (SCR) network**. The network maps the room from a short room scan and is trained on it; it then predicts the room coordinate of every image cell, and a 3D–3D RANSAC (Kabsch) on the measured depth turns those coordinates into the camera pose of every frame, smoothed over time. No tracker, no odometry, no keypoints. Results and discussion: `summary.md`; working notes and data guide: `note.md`; run index: `runs/README.md`.

## Problem and claim

Freehand 3D ultrasound needs the 6-DoF pose of every B-mode frame. External optical or EM trackers are accurate but expensive, line-of-sight constrained, and tie the exam to a prepared room. US-only sensorless estimation drifts far beyond the sub-millimetre budget set by the elevational beam width.

Given `{I_t_rgb, D_t, I_t_US}`, output `T_t ∈ SE(3)` in a room-fixed frame established at the start of the exam, from a single probe-mounted RGB-D camera — no markers, no fiducial pattern, no external infrastructure. Downstream: 3D volume reconstruction, and navigation relative to previously scanned anatomy.

**The goal is not a more accurate tracking system.** Sub-millimetre freehand US tracking already exists (optical ~0.5 mm, MLRecon 0.88 mm); beating it is neither likely nor interesting. The goal is a *useful* pose estimate with nothing outside the probe. Accuracy is a threshold to clear, not the axis of competition: miss it and the result is useless, clear it and the infrastructure argument becomes available.

**Where it stands** (error at the US image, mm; `summary.md` Tables F, G): without any tracker (room scan mapped by the network itself) 3XX **2.34**, volume shape **1.72** (three seeds 2.22–2.34); with Polaris labels for the room scan (oracle map) 1.85 / 1.57; classical system (SIFT anchors + SIFT odometry; its room-scan keyframes posed by Polaris) 3.11 / 2.47. New session (4XX, camera calibration from 3XX): shape 2.69 (best of all systems), absolute 7.92.

## Repository layout

| folder | what | files |
|---|---|---|
| `.` | **the system** | `scr_map.py` (map the room scan without a tracker), `scr_anchor.py` (`train`, `track`, `eval`), `scr.py` (network, labels), `dataloader.py`, `geometry.py`; `T_marker_cam.npy`, `calib_matrix.csv` (calibrations) |
| `tools/` | evaluation and figures | `us_analysis.py shape` (volume shape metric), `volume_pages.py` + `volume_3d.py` (interactive 3D pages), `volume_figure.py` (static volume figures), `slam_baseline.py` (RGB-D SLAM baseline: export, evaluate), `coverage_error.py`, `draw_scr_figures.py`, `draw_overview_tables.py`; the figures and `tables/` |
| `baselines/` | the systems we compare with | `anchoring.py` (classical SIFT anchors + odometry + pose graph; RPR anchor network), `anchoring_kabsch.py` (hybrid: SCR anchors in it), `anchor_classical.py`, `anchor_saliency.py`, and the RPR odometry stack `eval.py`, `poses.py`, `trajectory.py`, `model.py`, `loss.py` |
| `studies/` | studies not adopted | `scr_render.py` (rendered training views, `train --render-views`), `li_baseline.py` (Li et al., TBME 2024) |
| `runs/` | results behind every number in `summary.md` | checkpoints (`*.pt`) are not in git |

Run every command from the repository folder.

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

The hand–eye calibration (`T_marker_cam.npy`, marker → camera, mm) and the US calibration (`calib_matrix.csv`, TUS-REC format) are valid for all recordings with this probe and mount. Do not use the 1XX collection (broken depth). Sessions: `note.md` section 3.

Polaris is used to evaluate, and by the code to select the usable rows (rows with a marker pose); the system without a tracker does not use it otherwise, except for the camera calibration (below).

## 3. Quick check (a few minutes, any GPU)

```bash
export DATA=/path/to/data
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 --out runs/quickcheck \
  --epochs 3 --max-frames 200 --batch-size 2 --workers 2 --check-every 3 --check-frames 10 \
  --eval-root $DATA/train_3XX --eval-runs run-316
```

It should print the frames found, one line per epoch, and an evaluation table (errors of several cm: three epochs on 200 frames only test the pipeline).

## 4. The pipeline without a tracker

Five commands: map the room scan, train on it, track the sweeps, measure, look.

```bash
export DATA=/path/to/data
# 1. map: the network builds the room-scan poses itself (about 30 min on an A4500)
python scr_map.py --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/map-3XX
# 2. train the room model on the map's poses (about 40 min)
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --map runs/map-3XX --out runs/v2map-3XX
# 3. track every sweep frame with the network alone (applies the map's camera calibration by itself)
python scr_anchor.py track --ckpt runs/v2map-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/track-v2map-3XX
# 4. volume shape and relative motion at the US image
python tools/us_analysis.py shape --json runs/track-v2map-3XX/poses/*.json --out runs/track-v2map-3XX/shape.md
# 5. interactive 3D pages of each sweep (true vs estimated volume)
python tools/volume_pages.py --test-root $DATA/train_3XX --track runs/track-v2map-3XX --out runs/track-v2map-3XX/pages/3XX
```

**1. `scr_map.py`** (ACE0-style, with depth; figure `tools/scr_mapping.png`):
- *seed:* one room-scan frame defines the map; the frames of the 2 s around it join by frame-to-frame depth ICP (geometry only).
- *rounds:* train the network on the mapped frames, localise their neighbours with it (Kabsch RANSAC), extend the map edges by depth ICP; until a round adds < 0.5 % of the frames. A final pass localises every frame with the last network.
- *pose graph:* depth-ICP edges between frames 1–30 apart and loop closures (frames that see the same part of the room > 2 s apart or in the other scan), the network's poses as loose priors; robust least squares (`--no-graph`, `--loop-k 0` = no loops).
- *camera calibration:* the map is compared with Polaris after one rigid alignment plus one fixed camera-frame transform, the probe's camera calibration (Polaris gives the camera pose through the hand–eye calibration, the map from the camera itself). It is saved in `map.json`, kept out of the labels, and applied by `track`. It is the one place where Polaris enters: like any probe calibration it is measured once per probe. The report also fits it on each scan alone (held out on the other) and checks the camera/Polaris timing.
- *outputs:* `map_report.md` (map growth per round, map error against Polaris per stage: scene points 1 m ahead, camera position, rotation, 1 s relative motion; calibration and checks), `map.json`, `poses_<scan>.json` (labels), `network_poses.npz` (the network's poses before the pose graph), `map.pt` (the mapping network).
- *new session, same probe:* `--cam-calib-from runs/map-3XX/map.json` reuses that map's camera calibration instead of fitting one, so the new session's Polaris only aligns the map for the evaluation (how 4XX is tested).
- `--from <map folder> --out <new folder>` runs the pose graph again on an existing map (its network poses; ICP edges cached in `graph_edges.npz`, `graph_loops.npz`), e.g. with `--loop-k 0` or another `--graph-prior-mm`: minutes. `--realign` re-aligns a map's poses (no mapping).

**Without a tracker on a new session with the same probe** (4XX): add `--cam-calib-from runs/map-3XX/map.json` to step 1; steps 2–5 are unchanged.

**Ablations of step 1** (3XX, `summary.md` Table F): `--loop-k 0` (no loop closures), `--no-cam-calib` (no camera calibration), `--no-graph` (no pose graph); with `--from runs/map-3XX --out <new folder>` they reuse the existing map (minutes), then train and track as in steps 2–3.

**3. `track`** writes `scr_track.md` (error at the US image: raw and smoothed over 0.25–2 s; the system uses 2 s), `scr_track.json`, `poses.npz` (raw poses; a second run only re-smooths), and `poses/fold0_<sweep>_scr-track.json` (the system's poses per sweep, camera and US image, predicted and Polaris), which steps 4 and 5 read. `--lags 0.25` adds real-time smoothing.

## 5. The benchmark with Polaris labels

The same network with the room-scan poses from Polaris (the paper's main results, `summary.md` 3–4): train (25–50 min; `train`'s defaults are the final recipe v2 since 2 Nov 2026), evaluate its anchors (one frame per second), track.

```bash
python scr_anchor.py train --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/v2-3XX
python scr_anchor.py eval  --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX                  # anchors, Kabsch (default)
python scr_anchor.py eval  --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX --solver pnp     # anchors, PnP without depth
python scr_anchor.py track --ckpt runs/v2-3XX/best.pt --test-root $DATA/train_3XX --every 2 --out runs/track-3XX
```

Outputs of `train`: `config.json` (all settings), `history.json` (loss and fit check per epoch), `best.pt`; of `eval`: `eval_<test>[_kabsch]/scr_eval.md` / `.json`. Coverage analysis of an evaluation: `python tools/coverage_error.py runs/v2-3XX/eval_train_3XX_kabsch/scr_eval.json --out runs/coverage_3XX.md`.

The v1 recipe: `--head small --label-max-depth 3000 --keep-depth-edges`. Study options of `train` (`summary.md` 4, none adopted): `--freeze-encoder` (head only, ACE-style), `--render-views 0.5` (rendered views, `studies/scr_render.py`; `--render-source frames` from the nearest real frames; writes `render_preview.jpg`), `--confidence` with `track --weighted`, `--scan-seconds S` (first S s of each scan), `--aug-scale 0.67 1.5 --aug-rot 15`, map extension (sweeps added to `--scan-runs`, labelled with Polaris or with `--label-poses <poses JSON>`). `python scr_anchor.py train -h` lists everything.

## 6. Baselines (classical and hybrid systems)

Need two rgbd-us **result folders** (no rgbd-us code): the odometry run with its classical odometry caches in `preds/` (`runs/rpr-rgb-gap8-12XX-gru8` for 2XX/3XX, `runs/rpr-rgb-gap8-123XX-gru8` for 4XX) and the anchor pairs (`runs/anchor-pairs/`). Set `ODO` to the folder that holds them (anchoring writes its trajectories into `$ODO/<odometry run>/preds/`):

```bash
export DATA=/path/to/data ODO=/path/to/rgbd-us/runs
# classical system: SIFT anchors + SIFT odometry + pose graph
python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 \
  --root $DATA/train_3XX --scan-runs room-301 room-302 --test-root $DATA/train_3XX \
  --odometry-source classical-vo-train_3XX --odometry $ODO/rpr-rgb-gap8-12XX-gru8 --pairs $ODO/anchor-pairs/pairs_3XX.json \
  --pgo --start anchor --out runs/sys-classical-r-3XX
# hybrid: SCR anchors every 1 s + SIFT odometry + pose graph
python baselines/anchoring_kabsch.py -- evaluate --anchor scr --scr-ckpt runs/v2-3XX/best.pt --gate-recover 3 \
  --root $DATA/train_3XX --scan-runs room-301 room-302 --test-root $DATA/train_3XX \
  --odometry-source classical-vo-train_3XX --odometry $ODO/rpr-rgb-gap8-12XX-gru8 --pairs $ODO/anchor-pairs/pairs_3XX.json \
  --pgo --start anchor --out runs/sys-v2r-3XX
# 3D pages and shape: the single network vs the classical system vs odometry only (same rows for all)
python tools/volume_pages.py --test-root $DATA/train_3XX --track runs/track-3XX \
  --anchoring runs/sys-classical-r-3XX/anchor_eval_classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-train_3XX.json \
  --extra classical-vo-train_3XX --labels "classical anchors + classical odometry" "classical odometry only" --out runs/volume3d/3XX
python tools/us_analysis.py shape --json runs/volume3d/3XX/poses/*.json --out runs/shape-3XX.md
```

**Classical anchors on our own tracker-free map:** add `--map runs/repro/map-3XX` to the classical command: the keyframes are posed by that map (times its camera calibration) instead of Polaris.

**RGB-D SLAM baseline (ORB-SLAM3).** Build once on the training PC. No sudo needed: the libraries come from a conda environment, Pangolin is installed into it, ORB-SLAM3 is built in `/data2/u0137815/ORB_SLAM3`. Headless: the viewer is switched off.

```bash
# 1. libraries (conda-forge), and the compilers that match them
conda create -n orbslam -c conda-forge -y c-compiler cxx-compiler make "cmake<4" pkg-config eigen=3.4 "libopencv<5" libboost-devel glew libglu libgl-devel libopengl-devel libglx-devel libegl-devel xorg-libx11 xorg-libxext
conda activate orbslam
export CMAKE_PREFIX_PATH=$CONDA_PREFIX

# 2. Pangolin v0.6 (the version ORB-SLAM3 was tested with), into the environment
cd /data2/u0137815
git clone --branch v0.6 --depth 1 https://github.com/stevenlovegrove/Pangolin.git
cd Pangolin
export CXXFLAGS="$CXXFLAGS -include cstdint -include limits"        # newer gcc: old code relies on these headers (also for ORB-SLAM3)
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DBUILD_EXAMPLES=OFF -DBUILD_TOOLS=OFF -DBUILD_PANGOLIN_PYTHON=OFF -DBUILD_PANGOLIN_FFMPEG=OFF \
      -DOpenGL_GL_PREFERENCE=GLVND -DOPENGL_INCLUDE_DIR=$CONDA_PREFIX/include \
      -DOPENGL_opengl_LIBRARY=$CONDA_PREFIX/lib/libOpenGL.so -DOPENGL_glx_LIBRARY=$CONDA_PREFIX/lib/libGLX.so   # OpenGL from conda
cmake --build build -j8
cmake --install build

# 3. ORB-SLAM3
cd /data2/u0137815
git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git
cd ORB_SLAM3
sed -i 's/ORB_SLAM3::System::RGBD,true/ORB_SLAM3::System::RGBD,false/' Examples/RGB-D/rgbd_tum.cc      # no viewer
export OpenCV_DIR=$CONDA_PREFIX/lib/cmake/opencv4                                                    # conda's OpenCV
grep -rl 'find_package(OpenCV 4.4' --include=CMakeLists.txt . | xargs sed -i 's/find_package(OpenCV 4.4/find_package(OpenCV 4/'   # any 4.x, also in Thirdparty/
sed -i 's/-std=c++11/-std=c++14/g; s/CXX11/CXX14/g' CMakeLists.txt
sed -i 's/std::pair<const KeyFrame\*, g2o::Sim3>/std::pair<KeyFrame* const, g2o::Sim3>/' include/LoopClosing.h   # newer gcc
sed -i 's/make -j$/make -j8/' build.sh                                                                # unbounded -j runs out of memory
./build.sh

# 4. check: prints its usage line
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
./Examples/RGB-D/rgbd_tum
```

Before each use: `conda activate orbslam` and the `LD_LIBRARY_PATH` line. With sudo, the system packages (`libeigen3-dev libopencv-dev libboost-all-dev libglew-dev libgl1-mesa-dev`) replace step 1, and Pangolin installs with `sudo cmake --install build`.

Then per session: `tools/slam_baseline.py export` (room scans, then sweeps, as one RGB-D sequence), `rgbd_tum`, `tools/slam_baseline.py evaluate` (one alignment + camera calibration on the room scan, as our maps; `--cam-calib-from` for 4XX); commands in `note.md` 5. Frames ORB-SLAM3 loses have no pose and are counted.

Like-for-like variant `tools/orbslam3/rgbd_online.cc` (replaces `rgbd_tum`): writes the pose of each frame as it was tracked (`online.txt`, what a real-time system shows) besides the trajectory refined at shutdown, and with mode `localize` maps only the room scan and then localises with the map frozen (the information our system has). Build once, in `conda activate orbslam`:

```bash
cp $US/tools/orbslam3/rgbd_online.cc $ORB/Examples/RGB-D/
grep -q rgbd_online $ORB/CMakeLists.txt || printf '\nadd_executable(rgbd_online Examples/RGB-D/rgbd_online.cc)\ntarget_link_libraries(rgbd_online ${PROJECT_NAME})\nset_target_properties(rgbd_online PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/Examples/RGB-D)\n' >> $ORB/CMakeLists.txt
cd $ORB/build && cmake .. && make rgbd_online -j8
```

Run: `rgbd_online VOCAB SETTINGS SEQ ASSOCIATIONS OUT_DIR slam|localize N_MAP` with N_MAP = room-scan frames (`grep -c ',room-' SEQ/index.csv`); evaluate `OUT_DIR/online.txt` with `tools/slam_baseline.py evaluate --traj`.

Options of `anchoring.py evaluate`: `--start anchor` (no ground-truth pose at the start of a segment), `--gate-recover 3` (accept anchors again after a wrong one was accepted), `--scr-frames M` (one SCR anchor from M chain frames). Its other commands: `coverage`, `simulate`, `pairs` (the RPR anchor network itself is trained in rgbd-us).

## 7. Reproducing the results

Every number in `summary.md` names its run folder in `runs/`; `runs/README.md` explains the files, and each folder's `config.json` / `map.json` / `scr_track.json` records the command's settings. Training is not bit-exact across machines (cuDNN), so a retrained model lands within the seed spread (3XX 1.85–2.12 mm over three seeds); tracking a given checkpoint is deterministic (RANSAC seeded per frame).

Code history: `dataloader.py`, `geometry.py`, `scr.py` and the files in `baselines/` (except `anchoring_kabsch.py`) are copies of rgbd-us commit a5bf2ce; changed here: `anchoring.py` (`--gate-recover`, `--scr-frames`; its unused `train` command removed), `scr.py` (its own `train` / `eval` commands removed: `scr_anchor.py` replaced them). Moved on 3 Nov 2026 (older run folders record the old paths): `anchoring.py`, `eval.py`, `poses.py`, `trajectory.py`, `model.py`, `loss.py`, `tools/anchoring_kabsch.py`, `tools/anchor_classical.py`, `tools/anchor_saliency.py` → `baselines/`; `scr_render.py`, `tools/li_baseline.py` → `studies/`. Renamed on 28 Oct 2026: `tools/us_inplane.py`, `us_speckle.py`, `shape_error.py` → `tools/us_analysis.py inplane / speckle / shape`; `tools/li_repro.py`, `li_transfer.py` → `li_baseline.py repro / transfer`; `tools/scr_track.py` → `scr_anchor.py track`. Runs made before 23 Oct 2026 used options removed then (Huber loss, one-cycle schedule, Kabsch refinement); commit `3599239` has that code.









Pangolin needs the OpenGL headers (GL/gl.h) and libraries, which your conda environment doesn't have yet. You don't need sudo. Run this in the same terminal:

1. Install OpenGL into the conda environment


conda activate orbslam
conda install -c conda-forge -y libgl-devel libopengl-devel libglx-devel libegl-devel
ls $CONDA_PREFIX/include/GL/gl.h $CONDA_PREFIX/lib/libOpenGL.so $CONDA_PREFIX/lib/libGLX.so
The ls should list all three files.

2. Configure Pangolin again, pointing it at them


export CMAKE_PREFIX_PATH=$CONDA_PREFIX
cd /data2/u0137815/Pangolin
rm -rf build
cmake -B build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DBUILD_EXAMPLES=OFF -DBUILD_TOOLS=OFF -DBUILD_PANGOLIN_PYTHON=OFF -DBUILD_PANGOLIN_FFMPEG=OFF -DOpenGL_GL_PREFERENCE=GLVND -DOPENGL_INCLUDE_DIR=$CONDA_PREFIX/include -DOPENGL_opengl_LIBRARY=$CONDA_PREFIX/lib/libOpenGL.so -DOPENGL_glx_LIBRARY=$CONDA_PREFIX/lib/libGLX.so
cmake --build build -j8
cmake --install build
Then continue with the ORB-SLAM3 part from my last message.

If step 1 can't find those packages (older conda), use Mesa's software OpenGL instead, then run step 2 with the three OpenGL path flags replaced:


conda install -c conda-forge -y mesalib
# in step 2, instead of the GLVND / OPENGL_opengl / OPENGL_glx flags:
#   -DOpenGL_GL_PREFERENCE=LEGACY -DOPENGL_INCLUDE_DIR=$CONDA_PREFIX/include -DOPENGL_gl_LIBRARY=$CONDA_PREFIX/lib/libGL.so
ORB-SLAM3 runs with its viewer off, so OpenGL is only needed to compile and link; nothing is drawn at run time.