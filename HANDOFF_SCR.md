# rgbd-us: summary and data guide for the SCR project

Status 21 Oct 2026. Source project: `rgbd-us` (`note_RPR.md` there has every detail).

## 1. Summary

A probe-mounted RGB-D camera (RealSense, 1280 × 720) on a freehand ultrasound (US) probe; an NDI Polaris marker on the probe gives ground truth (~0.25 mm). The goal is the probe pose of every US frame with nothing outside the probe, using **odometry** between frames plus **anchors** (absolute poses against a room scan recorded before the exam), combined in a pose graph. Target: ~2 mm at the US image, which lies ~16 cm from the camera (1° of rotation ≈ 1.6 mm at the image bottom).

| mean error at the US image | 3XX (5 sweeps) | 4XX (blocks A–E) |
|---|---|---|
| classical odometry + classical anchors (SIFT + PnP-RANSAC with depth) | **3.3 mm** | **3.6–7.0 mm** |
| classical odometry only | 10.1 mm | 9.9–14.5 mm |
| classical odometry + our first SCR anchors | 6.5 mm | 12.0–21.4 mm |
| learned odometry + learned anchor network (pose regression) | 13.9 (8.5 adapted) mm | failed: 26–58 mm |

**Anchor accuracy** (camera position error, one frame every 1 s; this is the number SCR competes on):
- classical anchors: 2.6 mm (3XX), 3–7 mm (4XX);
- our first SCR: 9.8 mm (3XX), 16–26 mm (4XX);
- regression anchor network: 15 mm (3XX), 25–100 mm (4XX).

**Lessons**
- **Direct pose regression does not generalise to a new session.** The networks learn the session, not the geometry, and cannot reject outliers (moved objects, hands).
- **Our motion is tiny:** 2–5 mm per step, a sweep path of ~0.3–1 m within a few tens of cm, the camera 0.5–2.5 m from the scene. A learned regressor's error floor (~1–2 mm, 0.1–0.2° per step) is as large as the motion itself. Precision has to come from a geometric solve over many accurate correspondences. Public benchmarks (7-Scenes, TUM, KITTI) work at the cm–m scale and cannot show this.
- **Our first SCR underfits.** The setup:
  - EfficientNet-B0 with stride-8 and stride-16 features fused, plus a 1×1-conv head predicting room coordinates on a 45 × 80 grid from 360 × 640 RGB;
  - trained per room scan for 15 epochs, whole-image batches, a Huber loss on the 3D error, no depth input;
  - pose by PnP-RANSAC (10 px, ≥ 30 inliers).

  Its coordinate error is still 24–28 mm even on its own training frames.
- **Anchors need room-scan coverage of the sweep viewpoints:** 3XX covers 93 % of the sweep frames (a room-scan pose within 30 mm and 10°), 4XX only 0–14 %.
- **Room changes:** classical anchors survive a small change (8.5 mm) but fail on a large one (80 mm, only 21 % of anchors accepted). Our SCR failed on both (50–55 mm).
- **Odometry and anchors are both needed:** odometry alone drifts; anchors alone are accurate but jump from step to step. With good odometry, an anchor every 1–2 s is enough.

## 2. Where the data is

- **Training PC:** `/data2/u0137815/rgbd-us/data/train_<NXX>/` (all collections matched).
- **Recording PC:** `~/Desktop/rgbd-us/data/` (mostly unmatched raw data).
- Per collection: room scans `room-NXX/` (no US) and sweeps `run-NXX/`.

| collection | room scans | sweeps | role |
|---|---|---|---|
| 1XX (8 Oct) | room-101, 102 | run-101…112 | **do not use**: depth wrong (cable in front of the sensor), marker often lost |
| 2XX (9 Oct) | room-201, 202 (3.0 min) | run-201…212 (9.9 min) | main session, good coverage; validation sweeps run-205, run-211 |
| 3XX (9 Oct) | room-301, 302 (2.0 min) | run-313…317 (2.5 min) | **the clean test:** same room as 2XX, a few small objects moved |
| 4XX A (14 Oct) | room-401 (90 s), 402 (40 s) | run-401…408 | new session |
| 4XX B | room-403, 404 (40 s each) | run-409…412 | small rearrangement |
| 4XX C | room-405, 406 (40 s each) | run-413…416 | large rearrangement |
| 4XX D | C's scans | run-418…421, 423, 424 | second subject |
| 4XX E | C's scans | run-425…428 | occlusion (arm in view) |

## 3. Files and formats (per run)

| file | content |
|---|---|
| `frames.csv` | one row per RGB frame (~30 Hz); use this table |
| `rgb/NNNNNN.png` | colour 1280 × 720 (OpenCV reads BGR) |
| `depth/NNNNNN.png` | depth **aligned to the RGB image**, uint16, 1280 × 720, **mm**, 0 = invalid; reliable ~100–3000 mm |
| `depth_raw/` | the depth sensor's own 848 × 480 images; ignore |
| `camera_info.json` | RGB intrinsics `K` (fx ≈ 919.8, fy ≈ 919.5, cx ≈ 652.9, cy ≈ 373.6), no distortion; the same camera for all runs |
| `us/`, `us_roi.json` | US screen grabs 800 × 600, crop [121, 80]–[619, 440] (sweeps only) |
| `match_report.json` | matching quality: `pose_offset_ms` (already applied), `pose_lost`, `us_air_s` |

`frames.csv` columns:
- `timestamp`: RGB time (s);
- `rgb`, `depth`, `us`: paths relative to the run folder;
- **`tx, ty, tz`** (mm) and **`qx, qy, qz, qw`** (quaternion, scalar last) = `T_world_marker` in the Polaris frame, interpolated at the RGB time with the clock offset corrected. **Empty = marker lost: skip the row.**
- `us_air` = 1: probe not yet on the skin (start of a sweep);
- `us_repeat`: the US frame repeats the previous one.

**Camera pose:** `T_world_cam = T_world_marker @ T_marker_cam`. `T_marker_cam.npy` (copy it from the `rgbd-us` repo root: 4 × 4, translation in mm) is the hand-eye calibration, valid for 1XX–4XX (board-corner error 3.5 mm). The world is the Polaris frame. It is shared by all runs of a collection; the Polaris did not move between 2XX and 3XX.

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

rgb = cv2.imread(f"{run}/{r.rgb}")                                    # 720 x 1280 x 3, BGR
z = cv2.imread(f"{run}/{r.depth}", cv2.IMREAD_UNCHANGED).astype(np.float64)   # mm, aligned to rgb
v, u = np.nonzero((z > 100) & (z < 3000))
X = np.stack([(u - K[0, 2]) / K[0, 0] * z[v, u], (v - K[1, 2]) / K[1, 1] * z[v, u], z[v, u], np.ones(len(u))])
scene_coords = (T_wc @ X)[:3].T                                       # SCR labels: room coordinate (mm) of pixel (u, v)
```

Checked: room points from one frame, re-projected into a frame 1 s later, agree with that frame's depth within 7.9 mm (median), which is about the RealSense noise at 1–1.5 m. So poses, hand-eye and depth are consistent.

## 4. Suggestions for using the data with SCR

**Mapping set (what to train on)**
- **Train on a session's room scans,** with all usable frames rather than every 2nd. They are short: 2–3 min per session, 40–90 s per 4XX scan. Use every frame with a pose and depth, and sample pixels across all frames ACE-style rather than whole images.
- **Check coverage before blaming the model.** Our `tools/check_coverage.py` (rgbd-us) tells you which sweep frames have a room-scan view within 30 mm and 10°. On 4XX, most sweep frames do not, so expect larger errors there for any method. Report coverage next to the results.
- **Optional, clearly labelled extra mapping data:** frames from *other* sweeps of the same session, never the test sweep. For example, map on room scans + run-201…212 and test on 3XX. This shows how much more mapping data helps. Keep it separate from the room-scan-only result, which is the deployment case.

**Labels**
- **Depth is the label source.** Use only pixels with 100 mm < depth < 3000 mm. Depth noise grows roughly with distance squared: ~1 % at 1 m, worse beyond 2 m. Either down-weight far pixels (for example, weight 1/z²) or cap the depth at ~2 m for training labels.
- **Edges are wrong in depth.** Pixels at depth discontinuities (object borders) get mixed depths. Drop pixels whose 3×3 neighbourhood spans more than ~3 % of their depth.
- **Moving content:** hands and arms near the camera (< 300 mm), the operator's sleeve (4XX D/E), and the subject's body. In room scans these are rare; in sweeps they're common. Never train on them. At test time RANSAC should handle them.
- **Alternative or extra loss:** ACE-style reprojection error using only the poses, which also lets pixels without depth contribute. Combined with the depth-based 3D loss, it is a good way to compare whether depth labels or poses limit you.

**Inputs**
- **Resolution:** our 360 × 640 input on a stride-8 grid gives one prediction per 16 × 16 full-resolution pixels (~16 mm at 1 m). For mm-level poses, try 720 × 1280 input or stride 4. The PnP precision comes from many accurate correspondences, not from a coarse grid.
- **Depth at test time:** the strongest single lever. Either use it as a network input (RGB-D), or estimate the pose by 3D–3D RANSAC (Kabsch) between predicted room coordinates and the back-projected depth. DSAC* reports both variants.
- **Photometric augmentation** only (brightness, contrast, colour); no geometric augmentation unless the labels and intrinsics are transformed consistently.

**Test protocol** (as in rgbd-us, so numbers are comparable)
- Test on the sweeps of the mapped session: one frame every 1 s (30 rows), only rows with a pose and `us_air` = 0.
- Report the camera position error (mm) and rotation (°), median and p90, plus the share of frames solved.
- Splits:
  - **clean:** map 3XX room scans → test 3XX sweeps;
  - **validation:** map 2XX room scans → 2XX sweeps run-205 and run-211 (settings are chosen here only);
  - **new sessions:** 4XX A–E, each mapped on its own room scans (D and E use C's);
  - **scene change:** map 2XX → test 3XX; map 4XX A → test B (small change) and C (large change).
- **Numbers to beat** (classical anchors, same frames): 2.6 mm (3XX), 3–7 mm (4XX); with an outdated room scan, 10 mm (3XX on 2XX), 8 mm (B on A) and 80 mm (C on A).

**Quirks**
- `record_config.json` in 3XX still carries old run names (e.g. run-316 says `run-216`); trust the folder name.
- In 4XX, run-427 was run-422 and run-428 was run-417.
- The 4XX block folders `data/test_4XXA` … `test_4XXE` (training PC) are folders of links to `train_4XX`.

## 5. Literature for SCR
- Shotton et al., "Scene Coordinate Regression Forests for Camera Relocalization in RGB-D Images", CVPR 2013 (RGB-D SCR; 7-Scenes): https://openaccess.thecvf.com/content_cvpr_2013/html/Shotton_Scene_Coordinate_Regression_2013_CVPR_paper.html
- Brachmann & Rother, "Visual Camera Re-Localization from RGB and RGB-D Images Using DSAC" (DSAC*), TPAMI 2022: https://arxiv.org/abs/2002.12324
- Brachmann et al., "Accelerated Coordinate Encoding: Learning to Relocalize in Minutes using RGB and Poses" (ACE), CVPR 2023: https://arxiv.org/abs/2305.14059
- Wang et al., "GLACE: Global Local Accelerated Coordinate Encoding", CVPR 2024: https://openaccess.thecvf.com/content/CVPR2024/html/Wang_GLACE_Global_Local_Accelerated_Coordinate_Encoding_CVPR_2024_paper.html
- Brachmann et al., "Scene Coordinate Reconstruction" (ACE0), ECCV 2024 (SCR without given poses; relevant for a tracker-free map): https://arxiv.org/abs/2404.14351
- Brachmann et al., "On the Limits of Pseudo Ground Truth in Visual Camera Re-localisation", ICCV 2021 (benchmark ground truth is only cm-accurate): https://openaccess.thecvf.com/content/ICCV2021/html/Brachmann_On_the_Limits_of_Pseudo_Ground_Truth_in_Visual_Camera_ICCV_2021_paper.html
- Sattler et al., "Understanding the Limitations of CNN-based Absolute Camera Pose Regression", CVPR 2019: https://arxiv.org/abs/1903.07504
