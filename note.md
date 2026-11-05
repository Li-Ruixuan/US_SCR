# US_SCR: working notes

Status 4 Nov 2026. Results: `summary.md`. Run index: `runs/README.md`. Setup and commands: `README.md`. Source project: `rgbd-us` (`note_RPR.md` there). The earlier, longer version of these notes (status tables, experiment log) is in git commit 870a144.

## 1. Objective, questions, claims (updated 3 Nov 2026)

**Objective.** The pose of every freehand US frame from a probe-mounted RGB-D camera (RealSense D435i) alone, **with no tracker at any stage**: none during the exam and none to prepare the room. A 1–2 min room scan becomes a room model by one SCR network that makes its own training labels (`scr_map.py`); during the exam the same kind of network gives the camera pose of every frame (`scr_anchor.py track`). Accuracy is a threshold, not the competition: good enough for 3D reconstruction (a few mm at the US image, ~16 cm from the camera, 1° ≈ 1.6 mm; volume shape ~2–3 mm). Sub-millimetre optical tracking exists; the point is a useful pose with nothing outside the probe and no prepared room.

**What still uses Polaris.** (1) The camera calibration, one camera-frame transform per probe, now fitted on a room scan (3XX); like the US calibration it is measured once per probe, in deployment with a phantom. (2) The evaluation: ground truth, and one rigid alignment per session to put the map in the Polaris frame. (3) Row selection in the code (rows with a marker pose), an engineering shortcut. Nothing per room and nothing per exam.

**Research questions and current answers**

| | question | answer so far | evidence |
|---|---|---|---|
| RQ1 | Can a probe-mounted RGB-D camera and one learned model track freehand US with no tracker at any stage? | **Yes:** 3XX 2.34 mm at the US image, shape 1.72 mm (strict protocol 2.94); 4XX shape 2.69 mm, best of all systems; every frame mapped and tracked. 2XX validation is the exception (8.06 mm, poor map) | Results without a tracker, below |
| RQ2 | What does removing the tracker cost? | 3XX about 0.5 mm (2.34 / 1.72 vs 1.85 / 1.57 with Polaris labels); 4XX nothing in shape (2.69 vs 3.17) but 1.4 mm in absolute placement (7.92 vs 6.48). The network reproduces its labels, so the map is the bottleneck, not the network | below |
| RQ3 | Learned room coordinates vs the alternatives? | vs pose regression 8× better on anchors (strong); vs a classical SIFT pipeline on the same Polaris-posed map: better where the scan covers the sweeps, worse where not, shape better everywhere | Tables A–D |
| RQ4 | What decides the accuracy? | room-scan coverage of the sweep viewpoints; without a tracker the map: each mapping component is needed (without loop closures 5.77 mm, without the camera calibration 11.49, without both and the graph 13.26, vs 2.34) | Tables C, F |
| RQ5 | Do the US images help? | no (10 tests, Li et al. reproduced) | summary 6 |

**Claims.** The main claim is the tracker-free system; the earlier claims (summary 1.1, all with Polaris-posed maps) now describe its tracking part.

| | claim | evidence | strength | state with it |
|---|---|---|---|---|
| **C0** | **No tracker at any stage:** a 1–2 min room scan, one SCR network that labels itself, then every frame tracked | 3XX 2.34 / 1.72 mm (Polaris labels 1.85 / 1.57; classical with a Polaris-posed map 3.11 / 2.47); strict 2.94 (Polaris labels 2.98, classical 3.0); 4XX shape 2.69, best of all systems on every block | strong for shape, moderate for absolute | probe calibration fitted with Polaris once; 4XX absolute 7.92 vs 6.48 / 4.76; 2XX validation map failed (8.06 vs 3.35); three seeds 2.22–2.34 |
| C1 | One network on every frame replaces odometry + anchors | all 7 splits (Polaris maps) | strong | |
| C2 | Room coordinates + geometric solver beat pose regression | anchors 8× more accurate on 3XX and 4XX | strong | |
| C3 | Room-scan coverage decides the accuracy | covered 4.1 vs uncovered 13.4 mm; real views 4XX A 5.6 → 2.0 | strong | |
| C4 | SCR uses all room scans of the day despite moved objects; feature matching cannot | 4XX B–E 6.82 → 5.53 vs 4.90 → 13.93 | strong | pooling decided on test blocks |
| C5 | Smoother tracking and better volume shape than classical | every split | strong / moderate | shape metric introduced after the 4XX gap |
| C6 | The US images add nothing | 10 tests | strong (this setup) | |
| C7 | Real time | 0.25 s delay = offline | moderate | replayed, not live |

**Not claimed:** one network trained end to end (one SCR network + exact geometry: Kabsch, ICP, pose graph; deliberate, pose regression failed; see "End to end?" below); as accurate as Polaris labels; better than classical in new sessions with short scans; generalisation to new rooms (trained per room by design); a fully Polaris-free workflow (the calibration).

**End to end? (4 Nov)** The steps after the network, and whether each could become part of it:

| step | what it does | into the network? | verdict |
|---|---|---|---|
| Kabsch RANSAC + inlier gate | pose from the predicted room coordinates and the measured depth | **yes:** Kabsch is differentiable (SVD); RANSAC becomes differentiable with soft hypothesis selection (DSAC, DSAC* end-to-end stage, which includes RGB-D Kabsch). Fine-tune the network with a pose loss through it | the only one worth trying; expected gain small (the network already reproduces its labels; the map is the bottleneck); keeps the solver, so it is "end-to-end trained", not "one network" |
| temporal smoothing | 2 s window (0.25 s delay in real time) | possible: a recurrent / Kalman layer over the poses (KFNet, CVPR 2020) | little to gain (jitter 0.90 vs Polaris labels 0.93), risk of lag; no |
| camera calibration X | one fixed camera-frame transform per probe | as 6 learnable parameters only with a reference (Polaris or a phantom) in the loss: it is not observable from the camera alone | stays a calibration, like the US calibration |
| mapping (seed, rounds, ICP, pose graph, loops) | makes the training labels | joint training of network + poses (ACE0's pose refinement) | tried: made the map worse (8.4 → 8.9 mm); a learned bundle adjustment would still need geometry; no |
| whole pipeline as one feed-forward model | images → poses with no per-room training (DUSt3R / MASt3R / VGGT-type) | a different method: generic, cm-level, no per-room map | a comparison at most, not our system |

Position for the paper: like DSAC*, ACE and ACE0, the system is a hybrid on purpose: the network learns the room (the hard, appearance part); exact geometry does what is known exactly (rigid fit on measured depth, ICP, pose graph). End-to-end pose regression was tested and is 3–8× worse (claim C2). An end-to-end fine-tune through a differentiable Kabsch is an optional ablation (task 6 in section 2).

**Gap in the evidence.** Every classical comparison uses a Polaris-posed map: the classical system's keyframe poses come from Polaris (`baselines/anchoring.py`). Only classical odometry is tracker-free (shape 6.23 vs our 1.72). A reviewer will ask "why not RGB-D SLAM?": the missing baseline is an off-the-shelf RGB-D SLAM (e.g. ORB-SLAM3 RGB-D) on the room scan + sweeps, scored after the same one alignment per session. A cheap internal step: the classical anchors on our own tracker-free map (same map, network vs SIFT).

**Results without a tracker (3 Nov; `runs/repro/`, `runs/map-*`, `runs/track-v2map-*`).** Parity: the cleaned code reproduces the old numbers exactly (`runs/parity/`: 1.85 / 1.57; classical 3.11 / 2.47).

| split | map: scene pts / camera / 1 s motion (mm) | US absolute (jitter) | shape | Polaris labels | classical |
|---|---|---|---|---|---|
| 3XX (repro, loops) | 2.6 / 2.0 / 1.5 | **2.34** (0.90) | **1.72** | 1.85 / 1.57 | 3.11 / 2.47 |
| 3XX ablation: − loop closures (`repro/*-noloops`) | 4.5 / 5.2 / 1.5 | 5.77 (1.05) | 3.18 | | |
| 3XX ablation: − camera calibration (`repro/*-nocalib`) | 6.4 / 10.4 / 3.4 | 11.49 (1.06) | 4.08 | | |
| 3XX seeds 1 / 2 | 2.7 / 2.0 / 1.5; 2.7 / 1.9 / 1.4 | 2.22 / 2.25 (seeds 0–2 mean **2.27**) | 1.75 / 1.70 (mean **1.72**) | seeds 1.85–2.12 | |
| 3XX same rows as classical | | 2.35 | 1.73 | | 3.11 / 2.47 |
| 3XX real time (1 s window, 0.25 s delay) / causal (0.25 s) | | 2.34 (0.90) / 2.42 (1.13) | | 1.86 / 1.95 | |
| 3XX strict (room-301 only, own calibration) | 2.6 / 2.2 / 1.9 | **2.94** (1.17) | 2.18 | 2.98 (1.18) | 3.0 |
| 2XX validation (3XX calibration) | 6.7 / 8.3 / 3.6 (p90 31.2) | 8.06 (2.57) | 6.93 | 3.35 (1.20) | 4.2 |
| 4XX A / B / C / D / E (own scans, 3XX calibration) | 3.1–3.9 / 3.0–4.8 / 1.4–2.4 | 5.04 / 6.55 / 9.40 / 11.54 / 7.07, mean **7.92** | 2.94 / 2.40 / 2.05 / 3.10 / 2.98, mean **2.69** | 6.48 / 3.17 | 4.76 / 3.34 |
| 4XX real time (1 s window, 0.25 s delay / causal) | | 5.01 / 6.54 / 9.41 / 11.61 / 7.05 = offline; causal ≤ +0.2, step +0.3–0.4 | | | |
| 4XX same rows as classical | | 4.99 / 6.55 / 9.41 / 11.59 / 7.09, mean 7.93 | 2.99 / 2.41 / 2.12 / 3.09 / 3.05, mean **2.73** | | 4.22 / 3.38 / 4.85 / 6.32 / 4.99 (4.75); shape 3.10 / 2.47 / 3.36 / 3.61 / 4.15 (3.34) |
| 4XX pooled scans of the day, B / C / D / E | 4.0–4.3 / 5.7–5.9 / 1.9 | 8.08 / 10.69 / 14.00 / 10.62 | 2.53 / 2.21 / 3.98 / 3.15 | pooled 3.76 / 3.98 / 8.46 / 5.92 | |

- Loop closures: on the same 3XX map, scene points 4.5 → 2.6 mm, camera 5.2 → 2.0 mm, rotation 0.55° → 0.19° (`runs/repro/map-3XX-noloops`). Adopted (default).
- Probe calibration 31.7 mm, 1.51° (3XX); per scan 32.8 / 31.0 mm, 1.52° / 1.57° (each valid on the other scan); strict room-301 33.0 mm, 1.51°; 4XX scans 30–34 mm but 1.9–2.05°. No camera–Polaris timing offset (best +3 to +9 ms everywhere).
- 3D pages, 3XX (`runs/repro/volume3d/index.html`): mean pixel error over the compounded volumes 2.5 (no tracker) vs 3.2 (classical) vs 10.1 (odometry only); per sweep 3.0 / 2.5 / 2.5 / 1.9 / 2.8.
- 2XX validation fails: round 1 places 48 % of the frames, round 2 makes the map worse (camera 18.6 → 22.1 mm), the per-scan calibrations disagree (0.93° vs 1.89°) and the 1 s motion has a 31 mm p90, so some frames were joined wrongly and the pose graph did not fix them. 2XX has the longest scans (3 min, 5,366 frames). To investigate before the paper.
- Seeds (`runs/repro/*-seed1/2`): 2.34 / 2.22 / 2.25 mm, shape 1.72 / 1.75 / 1.70, calibration 31.2–31.7 mm and 1.51–1.52°: spread 0.12 mm, smaller than with Polaris labels (1.85–2.12).
- 4XX on the same rows as classical (`runs/shape-trackerfree-4XX-samerows.md`): shape better than classical on every block (2.73 vs 3.34), out-of-plane over 1 s equal or better (0.53–0.83 vs 0.63–1.02); absolute behind (7.93 vs 4.75).
- 4XX pooled scans without a tracker (`runs/map-pool-4XX*`, `runs/track-v2map-pool-4XX*`): worse on every block in absolute and shape; the pooled maps are worse (camera 5.7–5.9 vs 3.0–4.8 mm) because the scans of a room whose objects moved between blocks must be joined into one map. With Polaris labels pooling helped (each scan's labels are right on their own). Verdict: without a tracker, each block's own scans.
- 3D pages complete (`runs/volume3d-trackerfree/index.html`): pixel error over the compounded volumes 4XX A 5.7 / B 6.4 / C 9.9 / D 12.2 / E 7.5 (classical 4.4 / 3.7 / 5.3 / 7.2 / 5.2; it follows the absolute error), strict 3.3.
- Clean ablations (4 Nov, same map code, one component removed): without loop closures 5.77 / 3.18 (map camera 5.2 mm, rotation 0.55°); without the camera calibration 11.49 / 4.08 (map camera 10.4 mm, 1 s motion 3.4 mm). The calibration also matters for the shape: a camera-frame rotation error moves the US image differently as the probe turns. Every component is needed (summary Table F).
- 4XX real time: 0.25 s delay = offline on every block; causal: median ≤ +0.2 mm, step over 8 rows +0.3–0.4 mm.
- `summary.md` Tables F (ablations) and G (every split) and `tools/tables/table_F.png`, `table_G.png` hold the final numbers. Open tasks: section 2.

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

The map without a tracker is the target approach (3 Nov). Done by 4 Nov: reproduction from scratch, three seeds, loop closures and camera calibration ablations, strict, 2XX, 4XX (own and pooled scans, real time), 3D pages.
<<<<<<< HEAD
 
=======

**Still to run or build (4 Nov)**

| # | task | type | status |
|---|---|---|---|
| 1 | 4XX C / D placement: camera calibration refitted on 4XX's scans (diagnostic: uses 4XX Polaris), retrain, track | analysis | commands below |
| 2 | RGB-D SLAM baseline (ORB-SLAM3 RGB-D) on room scans + sweeps, same alignment + calibration on the room scan | comparison (the reviewer question) | `tools/slam_baseline.py` (export / evaluate); build ORB-SLAM3 once |
| 3 | classical anchors on our own tracker-free map (same map, network vs SIFT) | comparison | `baselines/anchoring.py evaluate --map <map folder>` |
| 4 | why the 2XX map fails: each scan alone, stricter joining, own calibration (2XX is validation: settings may be chosen on it) | analysis | commands below |
| 5 | static 3D volume figures (true, tracker-free, after the rigid fit, overlays; also classical) | figure | `tools/volume_figure.py` |
| 6 | end-to-end fine-tune through a differentiable Kabsch (DSAC*-style) | ablation, optional | not written |
| 7 | session with ~1 min room scans along the exam viewpoints; live run; RGB-only variant | data, future | recording / hardware |

>>>>>>> 4d7f324652f0257491ab9833c48749fa06cd4cc9

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


**Sensor and labels:** D435i, 50 mm stereo baseline, depth noise ~ distance² (under ~2 % at 2 m), mostly along the ray. Room points re-projected across frames 1 s apart agree within 7.9 mm (median) at 1–1.5 m. The 3.5 mm hand-eye error makes labels view-dependent. Never train on hands/arms, the sleeve (4XX D/E) or the subject.

**Quirks:** `record_config.json` in 3XX carries old run names (run-316 says `run-216`), trust the folder name; in 4XX, run-427 was run-422 and run-428 was run-417.

## 4. Literature

| | Shotton '13 | DSAC* (RGB-D) | ACE | GLACE | ACE0 | KFNet |
|---|---|---|---|---|---|---|
| model | forest, RGB-D features | FCN, stride 8 | frozen encoder + ~4 M 1×1 head | ACE + global feature | ACE, mapping without poses | SCR + Kalman filter over video |
| depth | input + Kabsch | labels + Kabsch | not used | not used | not used | not used |
| relevance | depth at test time | our pose solver | head size, augmentation | generalisation | Polaris-free maps | our single-network tracking |

Pose regression (PoseNet, MapNet, VLocNet, our RPR) stays behind structure-based methods (Sattler et al., CVPR 2019); learned systems that work are hybrids of learned correspondences and geometric solvers. Learned inlier weights + weighted Kabsch: Deep Global Registration (Choy et al., CVPR 2020). Recon2Servo (arXiv 2610.06010): training pairs rendered from a reconstruction, a frozen foundation encoder with LoRA; the rendering idea is our open task for coverage. US-only: Li et al. (TBME 2024), reproduced and negative on our data (`summary.md` 6).

**Our system vs ACE0** (Brachmann et al., ECCV 2024, [arXiv 2404.14351](https://arxiv.org/abs/2404.14351)). Borrowed: the self-mapping loop (start from one image, train, place more, repeat). Not checked in the paper: ACE0's exact inlier threshold and whether its code can use sensor depth.

| | ACE0 | ours |
|---|---|---|
| input | RGB image collection (may be unordered), no poses, intrinsics refined | RGB-D **video** (30 Hz), known intrinsics, measured depth |
| scale | from a monocular depth estimate at the start | metric, from the depth sensor |
| start | one seed image, identity pose | one frame + its ±2 s neighbours joined by depth ICP (one image alone: median 43 inliers on the next views) |
| training signal | reprojection error (2D) | direct 3D labels from depth + pose; 3D distance loss |
| network | ACE: frozen encoder + small MLP head, minutes per round | EfficientNet-B0 fine-tuned, stride 8 + 16, residual 1×1 head (3.0 M) |
| placing a frame | PnP-RANSAC, inlier threshold | Kabsch RANSAC on depth; ≥ 60 inliers + plausible motion vs a time neighbour; ≥ 400 far from the map |
| growing the map | relocalisation only | relocalisation + depth-ICP extension of the map edges |
| pose refinement | pose-refinement MLP trained jointly with the network | final pass + pose graph (ICP edges 1–30 frames apart, loop closures, network priors); joint refinement tried: worse (8.4 → 8.9 mm) |
| after mapping | the mapping network and its poses are the result | the poses label a final network trained from scratch (120 epochs) that tracks |
| calibration | camera intrinsics | probe camera calibration X (camera → probe), once per probe |
| evaluation | vs COLMAP, novel view synthesis | mm at the US image against an optical tracker; map error per stage; shape |
| use | poses for reconstruction | a tracking system: every frame, gate, smoothing, real time, US image pose |

**Similar work (4 Nov; abstracts only, to read in full)**
- ACE-SLAM (Alzugaray, Taher, Davison, arXiv 2512.14032, Dec 2025): RGB-D SLAM with a scene coordinate network as the map, mapping and tracking in real time; relocalisation and loop closure from the network. **The closest system**; ours: per-room training from a room scan, pose graph, probe calibration, mm evaluation.
- Cavallari et al. (CVPR 2017 arXiv 1702.02779; 3DV 2019 arXiv 1906.08744): scene coordinate models adapted to a new scene online, RGB-D, poses from an RGB-D SLAM, no offline training.
- Sun, Gilbertson, Anthony (MICCAI 2014, "Probe localization for freehand 3D ultrasound by tracking skin features"): camera on the probe, no tracker, skin-feature visual SLAM, scale from a sticker; ~0.91 mm, 0.55° per 10 mm of travel. **The key medical prior work.**
- Outside-in markerless probe tracking with a fixed RGB-D camera: MLRecon (arXiv 2603.00990, FoundationPose + SAM 2); Aliani et al. (EMBC 2025, D435 + FoundationPose).
- Literature-chat prompt for a full search: given in the session of 4 Nov (groups: SCR without poses, RGB-D SLAM, inside-out probe tracking, outside-in, sensorless US, SCR in medicine).








I checked every command against the scripts' argument definitions, and every flag exists. Run them on the training PC from the repo folder, in this order (quickest first). It's the same list as note.md section 2, with the 4XX steps written out in full.

<<<<<<< HEAD
 
=======

cd ~/US_SCR   # your repo on the training PC
export DATA=/data2/u0137815/rgbd-us/data ODO=/data2/u0137815/rgbd-us/runs
Task 5: static 3D volume figures (CPU, a few minutes each)

python tools/volume_figure.py --json runs/repro/volume3d/3XX/poses/fold0_run-316_scr-track.json runs/repro/volume3d/3XX/poses/fold0_run-316_anchored-pgo-classical-*.json --labels "no tracker (ours)" "classical" --rigid-fit --out runs/figures/volume_3XX_run-316.png
python tools/volume_figure.py --json runs/repro/volume3d/3XX/poses/fold0_run-313_scr-track.json runs/repro/volume3d/3XX/poses/fold0_run-313_anchored-pgo-classical-*.json --labels "no tracker (ours)" "classical" --rigid-fit --out runs/figures/volume_3XX_run-313.png
python tools/volume_figure.py --json runs/volume3d-trackerfree/4XXA/poses/fold0_run-406_scr-track.json runs/volume3d-trackerfree/4XXA/poses/fold0_run-406_anchored-pgo-classical-*.json --labels "no tracker (ours)" "classical" --rigid-fit --out runs/figures/volume_4XXA_run-406.png
python tools/volume_figure.py --json runs/volume3d-trackerfree/4XXC/poses/fold0_run-414_scr-track.json runs/volume3d-trackerfree/4XXC/poses/fold0_run-414_anchored-pgo-classical-*.json --labels "no tracker (ours)" "classical" --rigid-fit --out runs/figures/volume_4XXC_run-414.png
python tools/volume_figure.py --json runs/volume3d-trackerfree/4XXD/poses/fold0_run-420_scr-track.json runs/volume3d-trackerfree/4XXD/poses/fold0_run-420_anchored-pgo-classical-*.json --labels "no tracker (ours)" "classical" --rigid-fit --out runs/figures/volume_4XXD_run-420.png
Task 3: classical anchors on our own tracker-free map

python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 --root $DATA/train_3XX --scan-runs room-301 room-302 --test-root $DATA/train_3XX --odometry-source classical-vo-train_3XX --odometry $ODO/rpr-rgb-gap8-12XX-gru8 --pairs $ODO/anchor-pairs/pairs_3XX.json --pgo --start anchor --map runs/repro/map-3XX --out runs/sys-classical-trackerfree-3XX
python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 --root $DATA/test_4XXA --scan-runs room-401 room-402 --test-root $DATA/test_4XXA --odometry-source classical-vo-test_4XXA --odometry $ODO/rpr-rgb-gap8-123XX-gru8 --pairs $ODO/anchor-pairs/pairs_4XXA.json --pgo --start anchor --map runs/map-4XXA --out runs/sys-classical-trackerfree-4XXA
python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 --root $DATA/test_4XXB --scan-runs room-403 room-404 --test-root $DATA/test_4XXB --odometry-source classical-vo-test_4XXB --odometry $ODO/rpr-rgb-gap8-123XX-gru8 --pairs $ODO/anchor-pairs/pairs_4XXB.json --pgo --start anchor --map runs/map-4XXB --out runs/sys-classical-trackerfree-4XXB
python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 --root $DATA/test_4XXC --scan-runs room-405 room-406 --test-root $DATA/test_4XXC --odometry-source classical-vo-test_4XXC --odometry $ODO/rpr-rgb-gap8-123XX-gru8 --pairs $ODO/anchor-pairs/pairs_4XXC.json --pgo --start anchor --map runs/map-4XXC --out runs/sys-classical-trackerfree-4XXC
python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 --root $DATA/test_4XXD --scan-runs room-405 room-406 --test-root $DATA/test_4XXD --odometry-source classical-vo-test_4XXD --odometry $ODO/rpr-rgb-gap8-123XX-gru8 --pairs $ODO/anchor-pairs/pairs_4XXD.json --pgo --start anchor --map runs/map-4XXC --out runs/sys-classical-trackerfree-4XXD
python baselines/anchoring.py evaluate --anchor classical --gate-recover 3 --root $DATA/test_4XXE --scan-runs room-405 room-406 --test-root $DATA/test_4XXE --odometry-source classical-vo-test_4XXE --odometry $ODO/rpr-rgb-gap8-123XX-gru8 --pairs $ODO/anchor-pairs/pairs_4XXE.json --pgo --start anchor --map runs/map-4XXC --out runs/sys-classical-trackerfree-4XXE

python tools/volume_pages.py --test-root $DATA/train_3XX --track runs/repro/track-v2map-3XX --anchoring runs/sys-classical-trackerfree-3XX/anchor_eval_*.json --labels "classical anchors on our map" --out runs/volume3d-classical-ourmap/3XX
python tools/volume_pages.py --test-root $DATA/test_4XXA --track runs/track-v2map-4XXA --anchoring runs/sys-classical-trackerfree-4XXA/anchor_eval_*.json --labels "classical anchors on our map" --out runs/volume3d-classical-ourmap/4XXA
python tools/volume_pages.py --test-root $DATA/test_4XXB --track runs/track-v2map-4XXB --anchoring runs/sys-classical-trackerfree-4XXB/anchor_eval_*.json --labels "classical anchors on our map" --out runs/volume3d-classical-ourmap/4XXB
python tools/volume_pages.py --test-root $DATA/test_4XXC --track runs/track-v2map-4XXC --anchoring runs/sys-classical-trackerfree-4XXC/anchor_eval_*.json --labels "classical anchors on our map" --out runs/volume3d-classical-ourmap/4XXC
python tools/volume_pages.py --test-root $DATA/test_4XXD --track runs/track-v2map-4XXD --anchoring runs/sys-classical-trackerfree-4XXD/anchor_eval_*.json --labels "classical anchors on our map" --out runs/volume3d-classical-ourmap/4XXD
python tools/volume_pages.py --test-root $DATA/test_4XXE --track runs/track-v2map-4XXE --anchoring runs/sys-classical-trackerfree-4XXE/anchor_eval_*.json --labels "classical anchors on our map" --out runs/volume3d-classical-ourmap/4XXE
python tools/us_analysis.py shape --json runs/volume3d-classical-ourmap/*/poses/*.json --out runs/shape-classical-ourmap.md
Task 1: 4XX C/D with a camera calibration fitted on 4XX (about 1 h)

python scr_map.py --root $DATA/test_4XXC --scan-runs room-405 room-406 --from runs/map-4XXC --realign --out runs/map-4XXC-owncalib
python scr_anchor.py train --root $DATA/test_4XXC --scan-runs room-405 room-406 --map runs/map-4XXC-owncalib --out runs/v2map-4XXC-owncalib
python scr_anchor.py track --ckpt runs/v2map-4XXC-owncalib/best.pt --test-root $DATA/test_4XXC --every 2 --out runs/track-v2map-4XXC-owncalib
python scr_anchor.py track --ckpt runs/v2map-4XXC-owncalib/best.pt --test-root $DATA/test_4XXD --every 2 --out runs/track-v2map-4XXD-owncalib
python tools/us_analysis.py shape --json runs/track-v2map-4XXC-owncalib/poses/*.json runs/track-v2map-4XXD-owncalib/poses/*.json --out runs/shape-4XX-owncalib.md
Task 4: why the 2XX map fails (about 30 min per map)

python scr_map.py --root $DATA/train_2XX --scan-runs room-201 --cam-calib-from runs/repro/map-3XX/map.json --out runs/map-2XX-room201
python scr_map.py --root $DATA/train_2XX --scan-runs room-202 --cam-calib-from runs/repro/map-3XX/map.json --out runs/map-2XX-room202
python scr_map.py --root $DATA/train_2XX --scan-runs room-201 room-202 --cam-calib-from runs/repro/map-3XX/map.json --gate 120 --gate-far 800 --max-speed 300 --max-turn 60 --out runs/map-2XX-strictjoin
python scr_map.py --root $DATA/train_2XX --scan-runs room-201 room-202 --from runs/map-2XX --realign --out runs/map-2XX-owncalib
Compare the four map_report.md files. Then train and track only the best map; replace strictjoin below with whichever one it is:


python scr_anchor.py train --root $DATA/train_2XX --scan-runs room-201 room-202 --map runs/map-2XX-strictjoin --out runs/v2map-2XX-strictjoin
python scr_anchor.py track --ckpt runs/v2map-2XX-strictjoin/best.pt --test-root $DATA/train_2XX --test-runs run-205 run-211 --every 2 --out runs/track-v2map-2XX-strictjoin
Task 2: ORB-SLAM3 RGB-D baseline
Build it once; skip this step if you already did:


git clone https://github.com/stevenlovegrove/Pangolin.git ~/Pangolin && cd ~/Pangolin && ./scripts/install_prerequisites.sh recommended
cmake -B build && cmake --build build -j8 && sudo cmake --install build
git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git ~/ORB_SLAM3 && cd ~/ORB_SLAM3
sed -i 's/ORB_SLAM3::System::RGBD,true/ORB_SLAM3::System::RGBD,false/' Examples/RGB-D/rgbd_tum.cc
sed -i 's/find_package(OpenCV 4.4)/find_package(OpenCV 4)/; s/-std=c++11/-std=c++14/g; s/CXX11/CXX14/g' CMakeLists.txt
./build.sh
cd ~/US_SCR
3XX: the export already exists, so start with ORB-SLAM3 itself. It writes CameraTrajectory.txt in the folder it runs from.


export ORB=$HOME/ORB_SLAM3
cd runs/slam-3XX && $ORB/Examples/RGB-D/rgbd_tum $ORB/Vocabulary/ORBvoc.txt seq/camera.yaml seq seq/associations.txt && cd ../..
python tools/slam_baseline.py evaluate --root $DATA/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj runs/slam-3XX/CameraTrajectory.txt --out runs/slam-3XX
python tools/us_analysis.py shape --json runs/slam-3XX/poses/*.json --out runs/slam-3XX/shape.md
4XX, one block at a time. It uses the 3XX calibration, the same as for our 4XX maps. Run all three lines for each block:


python tools/slam_baseline.py export --root $DATA/test_4XXA --scan-runs room-401 room-402 --out runs/slam-4XXA/seq
cd runs/slam-4XXA && $ORB/Examples/RGB-D/rgbd_tum $ORB/Vocabulary/ORBvoc.txt seq/camera.yaml seq seq/associations.txt && cd ../..
python tools/slam_baseline.py evaluate --root $DATA/test_4XXA --scan-runs room-401 room-402 --seq runs/slam-4XXA/seq --traj runs/slam-4XXA/CameraTrajectory.txt --cam-calib-from runs/repro/map-3XX/map.json --out runs/slam-4XXA

python tools/slam_baseline.py export --root $DATA/test_4XXB --scan-runs room-403 room-404 --out runs/slam-4XXB/seq
cd runs/slam-4XXB && $ORB/Examples/RGB-D/rgbd_tum $ORB/Vocabulary/ORBvoc.txt seq/camera.yaml seq seq/associations.txt && cd ../..
python tools/slam_baseline.py evaluate --root $DATA/test_4XXB --scan-runs room-403 room-404 --seq runs/slam-4XXB/seq --traj runs/slam-4XXB/CameraTrajectory.txt --cam-calib-from runs/repro/map-3XX/map.json --out runs/slam-4XXB

python tools/slam_baseline.py export --root $DATA/test_4XXC --scan-runs room-405 room-406 --out runs/slam-4XXC/seq
cd runs/slam-4XXC && $ORB/Examples/RGB-D/rgbd_tum $ORB/Vocabulary/ORBvoc.txt seq/camera.yaml seq seq/associations.txt && cd ../..
python tools/slam_baseline.py evaluate --root $DATA/test_4XXC --scan-runs room-405 room-406 --seq runs/slam-4XXC/seq --traj runs/slam-4XXC/CameraTrajectory.txt --cam-calib-from runs/repro/map-3XX/map.json --out runs/slam-4XXC

python tools/slam_baseline.py export --root $DATA/test_4XXD --scan-runs room-405 room-406 --out runs/slam-4XXD/seq
cd runs/slam-4XXD && $ORB/Examples/RGB-D/rgbd_tum $ORB/Vocabulary/ORBvoc.txt seq/camera.yaml seq seq/associations.txt && cd ../..
python tools/slam_baseline.py evaluate --root $DATA/test_4XXD --scan-runs room-405 room-406 --seq runs/slam-4XXD/seq --traj runs/slam-4XXD/CameraTrajectory.txt --cam-calib-from runs/repro/map-3XX/map.json --out runs/slam-4XXD

python tools/slam_baseline.py export --root $DATA/test_4XXE --scan-runs room-405 room-406 --out runs/slam-4XXE/seq
cd runs/slam-4XXE && $ORB/Examples/RGB-D/rgbd_tum $ORB/Vocabulary/ORBvoc.txt seq/camera.yaml seq seq/associations.txt && cd ../..
python tools/slam_baseline.py evaluate --root $DATA/test_4XXE --scan-runs room-405 room-406 --seq runs/slam-4XXE/seq --traj runs/slam-4XXE/CameraTrajectory.txt --cam-calib-from runs/repro/map-3XX/map.json --out runs/slam-4XXE

python tools/us_analysis.py shape --json runs/slam-4XX*/poses/*.json --out runs/slam-4XX-shape.md
If ORB-SLAM3 crashes, or slam_eval.md shows few frames with a pose, send me the last 30 lines of its terminal output. ORB-SLAM3 starts a new map when it loses tracking, and that can break the evaluation.

Then push the results to me
This also stops git from tracking the ORB-SLAM3 frame links, which the export can recreate:


printf 'runs/slam-*/seq/rgb/\nruns/slam-*/seq/depth/\n' >> .gitignore
git rm -r --cached -q runs/slam-3XX/seq/rgb runs/slam-3XX/seq/depth
git add .gitignore runs/figures runs/sys-classical-trackerfree-* runs/volume3d-classical-ourmap runs/shape-classical-ourmap.md runs/map-4XXC-owncalib runs/v2map-4XXC-owncalib runs/track-v2map-4XX*-owncalib runs/shape-4XX-owncalib.md runs/map-2XX-* runs/v2map-2XX-* runs/track-v2map-2XX-* runs/slam-* runs/slam-4XX-shape.md
git commit -m "task results" && git push
>>>>>>> 4d7f324652f0257491ab9833c48749fa06cd4cc9
