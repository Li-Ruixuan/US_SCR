Context. I'm working on markerless pose estimation of a freehand ultrasound (US) probe, using an RGB-D camera (Intel RealSense, 1280 × 720) mounted on the probe and looking at the room. An NDI Polaris marker on the probe gives ground truth (~0.25 mm). The goal is the probe pose of every US frame with nothing outside the probe. The accuracy target is ~2 mm at the US image, which sits about 16 cm from the camera; 1° of rotation moves the bottom of the image by ~1.6 mm.

The system has three parts:

odometry between frames;
anchors: absolute poses against a room scan recorded with the same camera before the exam;
an offline pose graph that combines them.
In a previous project (rgbd-us) I compared learned and classical components. I now want to work on a scene coordinate regression (SCR) approach in this project.

What we found before (same data, Polaris ground truth):

Best system: classical odometry + classical anchors (SIFT + PnP-RANSAC with the depth). Mean error at the US image: 3.3 mm on the test set 3XX, 3.6–7.0 mm on a harder held-out session 4XX (new session, room changes, second subject, occlusion). Camera position error of the anchors: 2.6 mm (3XX), 3–7 mm (4XX).

Direct pose-regression networks failed to generalise to a new session; they learn the session, not the geometry. This held for relative pose regression (odometry) and for keyframe-to-frame regression (anchors): 13.9 mm on 3XX (8.5 mm after per-session fine-tuning), 26–58 mm on 4XX. A saliency and masking test showed they can't reject outliers (moved objects, hands).

Our first SCR attempt gave anchors of 9.8 mm (3XX) and 16–26 mm (4XX), every frame solved, but 3–5× worse than classical anchors. The setup:

EfficientNet-B0 with stride-8 and stride-16 features fused, plus a 1×1-conv head predicting room coordinates on a 45 × 80 grid from 360 × 640 RGB;
trained per room scan for 15 epochs, with targets from room-scan depth + Polaris poses and a Huber loss;
pose by PnP-RANSAC (10 px, ≥ 30 inliers).
It underfits: the coordinate error is still 24–28 mm even on its own training frames.

Our motion is very small: 2–5 mm per step, a sweep path of ~0.3–1 m within a few tens of cm, the camera 0.5–2.5 m from the scene. A learned regressor's error floor (~1–2 mm, 0.1–0.2° per step) is as large as the motion itself. Only methods ending in a geometric solve over many precise correspondences resolve it. Public benchmarks (7-Scenes, TUM, KITTI) work at cm–m scale and can't show this.

Room-scan coverage matters: the 4XX room scans covered only 0–14 % of the sweep viewpoints (a room-scan pose within 30 mm and 10° of the sweep frame), against 93 % in 3XX.

Anchors and odometry are both needed: odometry alone drifts (2–7 % of path for classical, 13–23 % for learned); anchors alone are accurate but jittery from step to step.

Data. The full guide is HANDOFF_SCR.md in the rgbd-us repo. The data is on the training PC at /data2/u0137815/rgbd-us/data/train_<NXX>/. Per run, frames.csv holds:

rgb: path to a 1280 × 720 PNG;
depth: path to the aligned depth, uint16 in mm, 0 = invalid;
tx, ty, tz (mm) and qx, qy, qz, qw (scalar last) = T_world_marker; empty = marker lost.
T_world_cam = T_world_marker @ T_marker_cam, with T_marker_cam.npy (mm) in the rgbd-us repo root; intrinsics are in camera_info.json.

Sessions:

room scans room-NXX are the mapping data; sweeps run-NXX are the test data;
2XX and 3XX: good room scans; 3XX is the clean test;
4XX blocks A–E: a hard case with short room scans, a small and a large room change, a second subject, occlusion;
do not use 1XX: its depth is broken.
Protocol for comparable numbers.

Train (map) on a session's room scans.
Test on its sweeps: one frame every 1 s (30 rows), only frames with a pose and us_air = 0.
Report the camera position error (mm) and rotation error (°) against the Polaris: median and p90, plus the share of frames solved.
Scene-change tests: map on the 2XX room scans and test on 3XX; map on 4XX A's scans and test on B and C.
What I want from you.

Review my SCR design against the literature: Shotton et al. CVPR 2013 (RGB-D SCR forests, 7-Scenes), DSAC* (TPAMI 2022, RGB and RGB-D), ACE (CVPR 2023), GLACE (CVPR 2024), ACE0 (ECCV 2024). Tell me which design choices most likely caused the 24–28 mm underfitting, and how to fix them. In particular:
a frozen pretrained encoder with ACE-style training on shuffled pixel buffers, against whole-image batches;
grid resolution and image resolution;
using the depth (as an input, as a 3D–3D RANSAC, or for refinement);
per-pixel confidence or uncertainty;
the reprojection loss against a 3D-coordinate loss;
the amount and coverage of mapping data.
Propose a step-by-step experiment plan that starts with the cheapest checks. For example: can the model fit its own training frames to a few mm? Does adding depth close most of the gap? Each step should have a clear pass/fail criterion against the classical anchors (2.6 mm on 3XX, 3–7 mm on 4XX).
Be honest about whether SCR can plausibly match SIFT + depth + PnP-RANSAC at this mm scale in an unchanged room, and where it could beat it: large room changes (classical anchors failed there with 80 mm), low texture, speed, no keyframe retrieval needed.
Keep the evaluation exactly comparable with the protocol above.
Start by asking me for anything you need from the existing SCR code or the data before proposing changes.




On the training PC:


cd <your US_SCR clone>
git pull
export RGBD_US=/data2/u0137815/rgbd-us DATA=/data2/u0137815/rgbd-us/data

# start S1 if it isn't running yet (check first: ps -eo pid,etime,cmd | grep "[s]cr_anchor")
nohup python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --out runs/s1-2XX \
  --eval-root $DATA/train_2XX --eval-runs run-205 run-211 > runs/s1-2XX.log 2>&1 &

tail -f runs/s1-2XX.log       # progress bar plus one line per epoch





# 1. Baseline: the scr.py recipe on 2XX (~25–30 min)
nohup python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --out runs/s1-base-2XX \
  --frame-step 2 --epochs 15 --sched onecycle --loss huber --no-fp32-head \
  --eval-root $DATA/train_2XX --eval-runs run-205 run-211 > runs/s1-base-2XX.log 2>&1 &

# 2. S1 (~1.5–2 h; can run alongside the baseline on the 20 GB card)
nohup python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --out runs/s1-2XX \
  --eval-root $DATA/train_2XX --eval-runs run-205 run-211 > runs/s1-2XX.log 2>&1 &

# 3. When both finish
git add runs && git commit -m "S0a + S1 results" && git push
The run times are estimates scaled from scr.py's 15–20 minutes on 3XX; 2XX has 1.5× as much room scan.

