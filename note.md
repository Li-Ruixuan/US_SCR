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
| 4XX C / D, calibration refitted on 4XX C (diagnostic, `*-4XXC-owncalib`, 5 Nov) | 3.0 / 1.6 / 1.4 | C **7.87** (was 9.40), D **9.58** (was 11.54) | 2.17 / 3.13 (was 2.05 / 3.10) | C 5.63, D 9.63 | |
| classical anchors on **our** tracker-free map (`sys-classical-trackerfree-*`, 5 Nov; pose graph) | same maps as above | 3XX 3.70 (same rows 3.65, shape 2.66; ours 2.35 / 1.73); 4XX A–E 6.5 / 4.3 / 5.0 / 7.4 / 5.7, mean **5.78** (ours 7.92) | 4XX: not yet run | | Polaris map 3.11 (3XX), 4.76 (4XX) |
| 2XX diagnostics (5 Nov, 3XX calibration): room-201 alone / room-202 alone / strict joining / own calibration | 6.6 / 5.0 / 4.8 (p90 31.2); 4.0 / 11.2 / 2.5 (p90 6.2); 9.2 / 10.7 / 5.7 (p90 32.2); 5.9 / 5.2 / 3.8 (p90 32.1) | strict joining 9.52 (run-205 14.2, run-211 4.9), was 8.13 | | | |

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
- **4XX C / D placement (5 Nov, task 1):** refitting the probe calibration on 4XX C's scans (32.0 mm, 1.91° vs 31.7 mm, 1.51° from 3XX; each 4XX C scan alone gives 1.97–2.02°, so it is consistent within the session) lowers the absolute error by 1.5 mm (C 9.40 → 7.87) and 2.0 mm (D 11.54 → 9.58); the shape does not change (2.17 / 3.13). D then equals the Polaris-labelled map (9.58 vs 9.63); C stays 2.2 mm above it (7.87 vs 5.63), which is the map's placement. So the 4XX gap is part calibration transfer (~0.4° between sessions), part map. For the paper: X is stable within a session but not exactly between sessions; a phantom calibration per session (or per day) would remove this part. Diagnostic only: it uses 4XX Polaris.
- **Classical anchors on our own map (5 Nov, task 3):** the same tracker-free map, SIFT + PnP instead of the network. 3XX (covering scans): SCR 2.35 / 1.73 vs SIFT 3.65 / 2.66 on the same rows: the network is better than feature matching on the same map. 4XX (poorly covering scans): SIFT 5.78 vs SCR 7.92 mean (SCR better on A, 5.04 vs 6.5; SIFT better on B–E): SIFT generalises to unseen viewpoints better. The 4XX gap to the classical system (7.92 vs 4.76) therefore splits into ~2.1 mm method (SCR vs SIFT on the same map) and ~1.0 mm map (self-made vs Polaris). The self-made map costs SIFT about as much as SCR on 3XX (3.11 → 3.70 vs 1.85 → 2.34). Still to run: 4XX shape (`volume_pages.py` per block, as for 3XX).
- **2XX map (5 Nov, task 4):** the problem is `room-201`. Alone it keeps the 31 mm p90 of the 1 s motion (some stretch is joined wrongly), while `room-202` alone is clean (p90 6.2 mm, scene points 4.0 mm). Stricter joining is worse (map 9.2 mm, tracking 9.52 vs 8.13). The own calibration helps the map a little (5.9 / 5.2 mm vs 6.7 / 8.3); not yet tracked. Next: find the bad stretch of room-201 (fast motion? textureless?), and train / track on the room-202 map (and on the own-calibration map) for run-205 / run-211 (2XX is validation, so the setting may be chosen here).
- **Volume figures (5 Nov, task 5):** `runs/figures/volume_*.png/.pdf` (3XX run-313, 316; 4XX A run-406, C run-414, D run-420). 3XX run-316: pixel error 1.9 mm (rigid fit 1.5) vs classical 2.6 (2.4); 4XX C run-414: 12.2 mm, after the rigid fit 2.9 (classical 4.6 / 3.7), the clearest picture of "right shape, wrong place". The title overlapped the view names (fixed 5 Nov; re-run to refresh). For the paper, use a subset of the rows (true, ours, ours after the rigid fit, overlay).
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
 

### 2.1 Recording plan, 5 Nov 2026 (session 5XX: same room, many views, several scene changes)

**Status (5 Nov):** A, B and C are recorded, up to `run-524`. The lighting block is dropped. Still to do: D, people moving in C's layout; then E, an empty room.

Done before recording:
- Probe, camera and marker mount unchanged since 14 Oct, so `T_marker_cam.npy` and the US calibration stay valid. No hand–eye recording is needed.
- US settings unchanged: Depth 9 cm, gain 48 %, 19 fps, Map 1, zoom 100 %.
- Polaris fixed for the whole session.
- **US target: a different phantom today** (type: [fill in]), not a forearm as in 2XX–4XX, so the US image content of 5XX differs from the earlier sessions; the camera tracking is comparable. The US calibration still holds (scanner settings unchanged). It assumes 1540 m/s, so a phantom with another speed of sound scales the image depth slightly: check the phantom's data sheet. The phantom stays at one place on the table within each block; if it moves, write it down, since the camera may see it.

**What this session answers**

| question | how | blocks |
|---|---|---|
| Q1 Coverage, cleanly: does a scan along the exam views fix the 4XX placement error (3XX: 93–96 % covered → 2.34 mm; 4XX: 0–14 % → 7.92 mm)? | the same sweeps with a map from a generic scan and from an exam-view scan | A, B, C |
| Q2 Views far from earlier sessions | 4 views per block (V1–V4); error against view and coverage | all |
| Q3 Large scene changes: own new scan vs outdated map | B and C sweeps with their own scans and with the previous block's map | B, C |
| Q4 People moving in the background | C's map on D's sweeps | D |
| Q5 Empty room, little texture: does a map of only walls and fixed furniture still localise? | E's own scans (generic and exam-view) on E's sweeps; also C's map on E's sweeps (extreme outdated map) | E |
| Q6 Scan before vs after the sweeps (strict protocol) | `room-503` after A's sweeps | A |

**Views** (same in every block; take a photo of each one in block A and stand on the same floor marks later; tape on the floor helps)

| view | probe and camera |
|---|---|
| V1 | the usual position and direction (as 3XX / 4XX) |
| V2 | same place, probe turned ~90° about the vertical: the camera sees another wall |
| V3 | probe turned ~180°: the camera sees the opposite wall (only if the marker stays visible to Polaris; otherwise a tilted view, camera ~30° up or down) |
| V4 | another place: other side of the bed, or the arm ~1 m away, the operator standing elsewhere |

Check every view once in block A with the Polaris status visible. Keep a view only if the marker stays tracked over the whole sweep path.

**Scene changes** (photograph the whole room from 2–3 fixed spots before and after each change; write down what moved)

| block | scene | what to change |
|---|---|---|
| A | the room as it is today | nothing; this is the reference |
| B | large rearrangement 1 | move or replace most small and medium objects in all four camera views: boxes, bottles, phantoms, papers, chairs, the cart; add 3–5 new textured objects. Big furniture (cabinets, bed, walls, screens) stays |
| C | large rearrangement 2 (very large) | B plus the furniture that can move: table / cart / chair positions, a cloth over one cabinet or shelf, posters on or off. Remove some textured items so a view has less texture. Walls and fixed cabinets stay |
| ~~lighting~~ | dropped | not recorded |
| D | C's layout, people moving | a second person walks, stands or moves a chair in the background during every sweep, mostly in the camera's view. Nothing else changes |
| E | empty room | take out every movable and complex device and object: carts, phantoms, boxes, screens that can be moved, small furniture. **Keep exactly in place:** the Polaris (don't bump it while carrying things out), the bed or table and the chair the subject needs, the US scanner and the recording PC. What remains is walls, door, windows and fixed cabinets |

**Order and names** (names follow recording order. If you add an extra scan or redo a sweep, give it the next free number and write it on the sheet; the plan below then shifts.)

| block | # | recording | length | how |
|---|---|---|---|---|
| A | 1 | `room-501` generic | 90 s | walk the room as in 4XX A, no attention to the exam views |
| | 2 | `room-502` exam views | 90 s | ~20 s per view V1–V4: hover along each sweep path in the air, at sweep height and angle, slowly, rocking ±10–15°, several passes. Coverage needs a scan pose within **30 mm and 10°** of the sweep pose; facing the same wall is not enough. The subject's arm is not on the table |
| | 3 | `run-501` (V1) | 60 s | first sweep, then **check coverage** (below) |
| | 4 | `run-502` … `run-508` | 60 s each | V1, V2, V2, V3, V3, V4, V4 |
| | 5 | `room-503` exam views, after the sweeps | 60 s | as #2 |
| B | 6 | rearrange, photos | | |
| | 7 | `room-504` generic, `room-505` exam views | 90 s each | as #1, #2 |
| | 8 | `run-509` … `run-516` | 60 s each | V1, V1, V2, V2, V3, V3, V4, V4; check coverage after `run-509` |
| C | 9 | rearrange, photos | | |
| | 10 | `room-506` generic, `room-507` exam views | 90 s each | as #1, #2 |
| | 11 | `run-517` … `run-524` | 60 s each | V1, V1, V2, V2, V3, V3, V4, V4; check coverage after `run-517` |
| D | 12 | C's layout unchanged, a second person in the background | | no new room scan: D uses C's (`room-506`, `room-507`) |
| | 13 | `run-525` … `run-528` | 60 s each | V1, V2, V3, V4, with the person moving throughout |
| E | 14 | empty the room (as above), photos from the same 2–3 spots | | |
| | 15 | `room-508` generic, `room-509` exam views | 90 s each | as #1, #2. In an empty room, also pass over the corners, the door and the window edges, which are what is left to recognise |
| | 16 | `run-529` … `run-532` | 60 s each | V1, V2, V3, V4; check coverage after `run-529` |


**Commands on the recording PC** (from the rgbd-us folder):
```bash
python3 tools/record_train.py --run room-501 --root ./data/train_5XX --no-us --duration 90
python3 tools/record_train.py --run room-502 --root ./data/train_5XX --no-us --duration 90
python3 tools/record_train.py --run run-501 --root ./data/train_5XX --duration 60 --no-match
# coverage of the first sweep of the block, from the raw Polaris poses (seconds):
python3 tools/check_coverage.py --root data/train_5XX --scans room-502 --sweeps run-501
python3 tools/check_coverage.py --root data/train_5XX --scans room-501 --sweeps run-501
``` 

**Log sheet** (fill in during recording)

| name | block | scan / sweep | view | length | coverage (exam-view / generic scan) | marker OK? | notes (what moved, light, person, marker lost, redo) |
|---|---|---|---|---|---|---|---|
 

**Analysis (rules fixed before seeing results)**
- Every map is made without a tracker (`scr_map.py`); probe calibration X from 3XX, as for 4XX. A 5XX-fitted X is a diagnostic only. 5XX is a test session: nothing is tuned on it.
- Q1: own generic scan vs own exam-view scan, on the same sweeps (A, B, C); the main result. Also generic + exam-view together.
- Q3: B with A's map, C with B's map and with A's map, against their own scans.
- Q4: D with C's map. Q5: E with its own generic and exam-view scans, and with C's map. Also the fraction of frames with a pose and the map error against Polaris. Q6: A with `room-503` only (and E with `room-510`, if recorded).
- Per block, also report the oracle map and the classical pipeline on the same scans, and ORB-SLAM3. Report per view: absolute, shape and coverage.


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
| 5XX (5 Nov) | A: room-501 generic (90 s), 502 exam views (90 s), 503 after (60 s); B: 504 generic (90 s), 505 exam views (60 s); C: 506, 507 (90 s each); E: 508 generic (90 s), 509 exam views (60 s) | A run-501–508, B 509–516, C 517–524, D 525–528 (C's scans), E 529–532; views per block V1, V1, V2, V2, V3, V3, V4, V4 (D, E: V1–V4) | same room, many views; B, C large rearrangements; D people moving; E empty room; **sweeps on a different phantom, not a forearm** (2.1); block folders `test_5XXA` … `E` (links, every room scan + the block's sweeps) |

Per run: `frames.csv` (one row per RGB frame, ~30 Hz: `timestamp`; `rgb`, `depth`, `us` paths; `tx, ty, tz` mm and `qx, qy, qz, qw` scalar last = `T_world_marker`, clock offset already applied, **empty = marker lost**; `us_air` = 1 probe not on the skin; `us_repeat` = 1 same US frame as the row before), `rgb/` 1280 × 720, `depth/` aligned to RGB, uint16 mm, 0 = invalid, reliable 100–3000 mm, `camera_info.json` (fx ≈ 919.8, fy ≈ 919.5, cx ≈ 652.9, cy ≈ 373.6, no distortion), `us/` + `us_roi.json` (sweeps), `match_report.json`; ignore `depth_raw/`.

**Camera pose:** `T_world_cam = T_world_marker @ T_marker_cam`, world = Polaris frame (not moved between 2XX and 3XX). **`T_marker_cam.npy` must be the rgbd-us one** (mm, board-corner error 3.5 mm). **US image pose:** `T_world_cam @ inv(T_marker_cam) @ rigid @ scaling` with `calib_matrix.csv` (TUS-REC format, 1-based pixels on the US crop resized to 640 × 480, 0.2295 × 0.2213 mm/px).
 

**Sensor and labels:** D435i, 50 mm stereo baseline, depth noise ~ distance² (under ~2 % at 2 m), mostly along the ray. Room points re-projected across frames 1 s apart agree within 7.9 mm (median) at 1–1.5 m. The 3.5 mm hand-eye error makes labels view-dependent. Never train on hands/arms, the sleeve (4XX D/E) or the subject.

**5XX raw check (5 Nov, before matching):** all 41 recordings complete (60 / 90 s, RGB 29.4–30.0 Hz), names match the configs. Marker lost: run-530 12.3 s (of 60), room-504 4.3 s, run-509 1.3 s, room-508 1.2 s, run-529 / 532 < 1 s, otherwise none. Not matched yet (no `frames.csv`, depth not aligned): `match_streams.py --apply-sync`, then `tools/check_session.py` (depth usable within 0.1–2 m, marker, clock offset, US).

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











6. ORB-SLAM3 on 3XX and 5XX A, run once with each A scan. First build ORB-SLAM3 once on the training PC, using the steps in README.md section 6. ORB-SLAM3 always writes CameraTrajectory.txt to its own folder, so run each evaluate straight after its SLAM run.


US=/data2/u0137815/US_SCR
python tools/slam_baseline.py export --root $DATA/train_3XX --scan-runs room-301 room-302 --out runs/slam-3XX/seq
python tools/slam_baseline.py export --root $DATA/test_5XXA --scan-runs room-502 --out runs/slam-5XXA-exam/seq
python tools/slam_baseline.py export --root $DATA/test_5XXA --scan-runs room-501 --out runs/slam-5XXA-generic/seq

cd /data2/u0137815/ORB_SLAM3
./Examples/RGB-D/rgbd_tum Vocabulary/ORBvoc.txt $US/runs/slam-3XX/seq/camera.yaml $US/runs/slam-3XX/seq $US/runs/slam-3XX/seq/associations.txt
cd $US
python tools/slam_baseline.py evaluate --root $DATA/train_3XX --scan-runs room-301 room-302 --seq runs/slam-3XX/seq --traj ~/ORB_SLAM3/CameraTrajectory.txt --smooth 1 --out runs/slam-3XX





cd ~/ORB_SLAM3
./Examples/RGB-D/rgbd_tum Vocabulary/ORBvoc.txt $US/runs/slam-5XXA-exam/seq/camera.yaml $US/runs/slam-5XXA-exam/seq $US/runs/slam-5XXA-exam/seq/associations.txt
cd $US
python tools/slam_baseline.py evaluate --root $DATA/test_5XXA --scan-runs room-502 --seq runs/slam-5XXA-exam/seq --traj ~/ORB_SLAM3/CameraTrajectory.txt $CAL --smooth 1 --out runs/slam-5XXA-exam

cd ~/ORB_SLAM3
./Examples/RGB-D/rgbd_tum Vocabulary/ORBvoc.txt $US/runs/slam-5XXA-generic/seq/camera.yaml $US/runs/slam-5XXA-generic/seq $US/runs/slam-5XXA-generic/seq/associations.txt
cd $US
python tools/slam_baseline.py evaluate --root $DATA/test_5XXA --scan-runs room-501 --seq runs/slam-5XXA-generic/seq --traj ~/ORB_SLAM3/CameraTrajectory.txt $CAL --smooth 1 --out runs/slam-5XXA-generic

python tools/us_analysis.py shape --json runs/slam-*/poses/*.json --out runs/shape-slam.md
--smooth 1 smooths the SLAM poses over 1 s, the same as our numbers. For 3XX, evaluate fits the camera calibration on the room scan, as our 3XX map did. For 5XX it reuses the 3XX calibration, as all our 5XX maps did.

If you run them all, a suggested order: 1, 2, 3, 4, 5, then 6.