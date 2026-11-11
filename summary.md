# Markerless US probe tracking with one scene coordinate regression (SCR) network: results

Status 11 Nov 2026. Claims and their evidence: 1.1. Overview tables of all tests: 1.2. Data: 2.1. Builds on `rgbd-us` (`note_RPR.md` there). Run index: `runs/README.md`. Working notes and data guide: `note.md`. The earlier, chronological version of this summary (sections 3.1–3.20, all intermediate tables) is in git commit 870a144.

## 1. Bottom line

| question | answer | evidence |
|---|---|---|
| **Final system** | **One SCR network on every frame + Kabsch RANSAC on the measured depth + temporal smoothing.** No odometry, no hand-crafted features, no tracker at test time. Each model trained on all room scans recorded that day up to its block. Error at the US image: 2XX val 3.35, **3XX 1.85 (three seeds 1.85–2.12)**, 4XX A 5.14, B 3.76, C 3.98, D 8.46, E 5.92 mm (own block's scans only: B 5.77, C 5.63, D 9.63, E 6.25) | 3.1, 4.3 |
| vs the classical system (SIFT anchors + SIFT odometry) | **Better where the room is well mapped** (3XX 1.85–2.12 vs 3.1 mm, every seed); **on par under the strict protocol** (map recorded before the sweeps: 2.98 vs 3.0 mm, smoother); **worse on new sessions with short room scans** (4XX mean 5.45 vs 4.76 mm, 1.15×; 1.4× before pooling the scans; C better, D and E worse); **volume shape better on every split** (Table D) | 3.1, 4.3, 4.7 |
| Why worse on 4XX? | **Room-scan coverage:** the 4XX scans see 0–14 % of the sweep viewpoints (3XX 93–96 %). With 1–2 earlier sweeps added to the map (Polaris-labelled), SCR beats classical on 4XX too (A 2.3 vs 3.2, D 4.5 vs 5.8 mm). Labelling those sweeps with the system's own poses does not work (A 5.3 → 5.0 mm). **Pooling the room scans of the same day** helps SCR without any labelling (B–E mean 6.82 → 5.53 mm) but ruins classical (4.90 → 13.93 mm): objects moved between the blocks, and SIFT matches the moved objects in the old scans confidently, while the network learns the static room | 4.3 |
| Is odometry needed? | **No.** On all 7 splits SCR alone, smoothed over 2 s, matches SCR + SIFT odometry in median (4XX mean 6.48 vs 6.54 mm) and is as smooth or smoother (step 0.82–1.68 vs 1.08–2.22 mm). Learned RPRNet odometry instead of SIFT is worse (+0.3–0.6 mm) | 3.1, 4.6 |
| Real time? | **Yes.** With a 0.25 s delay (window of the last 1 s) the results equal the offline 2 s smoothing (3XX 1.86 (0.93), 4XX mean 5.43 (1.06) mm); fully causal (no delay) the median is the same and the steps ~20 % larger (3XX 1.95 (1.18), 4XX 5.47 (1.28)), still as smooth as classical | 3.3 |
| How long must a room scan be? | **Where it goes matters more than how long.** 3XX with the first 20 / 40 / ~60 s of each scan: 3.00 / 2.03 / 1.85 mm (classical 3.1); 4XX A has 130 s of scans and still 5.14 mm, because they miss the sweep viewpoints | 4.3 |
| Why did the first SCR fail (24–28 mm)? | **Undertrained,** not unable: same network and data, 2XX val 15.8 → 5.1 mm by the training fix alone; depth at test time (Kabsch) → 3.4 mm | 4.1 |
| SCR vs pose regression (RPR anchor network) | **SCR 3–6× more accurate on every split**, always solves (RPR: 37–93 % accepted) | 4.2, 5 |
| Strict protocol (map recorded before the sweeps) | **On par with classical:** single network 2.98 (1.18) vs classical system 3.0 (1.34) mm on run-315…317 with the map on room-301 only; with both room scans 1.83 vs 2.9. Part of the 3XX advantage comes from room-302, recorded after the sweeps | 4.7 |
| Is the 4XX gap distortion or offset? | **A rigid offset of each sweep:** after a rigid fit, the single network's volume shape is better than classical's on every split (2XX 3.04 vs 3.98, 3XX 1.57 vs 2.47, 3XX strict 2.26 vs 2.59, 4XX 2.95 vs 3.34 mm with the pooled scans; each of A–E better) | 4.8 |
| Can the US images help? | **No.** In-plane registration is worse than assuming no motion; speckle measures out-of-plane distance (0.3–0.4 mm) but the camera is 2–5× better between nearby frames; Li et al. (reproduced on its own data: 21.4 vs 22.8 mm published) is no better than zero motion on ours, fine-tuned worse | 6 |
| Without a tracker? | **Yes.** The network maps the room scan itself (`scr_map.py`: depth ICP, pose graph with loop closures, camera calibration), its poses label the training. 3XX: **2.34 mm** at the US image, shape **1.72** (three seeds 2.22–2.34), against 1.85 / 1.57 with Polaris labels and 3.11 / 2.47 for the Polaris-mapped classical system; strict protocol 2.94 (Polaris labels 2.98, classical 3.0). 4XX (3XX calibration): shape 2.69, better than classical, absolute 7.92 (Polaris labels 6.48, classical 4.76). 2XX validation map failed (8.06). The camera calibration (one camera-frame transform per probe) is fitted once with Polaris | Tables F, G |
| Third session (5XX): what decides? | **Coverage, then the map.** With a scan along the exam views (the protocol) 2.28 mm in A (Polaris labels 1.85: removing the tracker costs 0.4 mm, as in 3XX), C 3.11, D 2.24; the same A sweeps with a generic scan that misses the exam views 13.57 mm, and still 10.95 with Polaris labels. With the views covered, the error follows the map (E, empty room: 5.85). People moving: no effect. An outdated map survives a large rearrangement (4.28) but not a very large one (41–59 mm); the inlier count flags it. 40 training epochs are enough | 4.9 |
| vs RGB-D SLAM (ORB-SLAM3, no tracker either) | **ORB-SLAM3 is better, also like for like.** Map from the room scan only, then frozen (localisation only, patched to relocalise), poses as tracked: 3XX 1.84 / 1.30 vs our 2.34 / 1.72 (absolute / shape), 4XX A–D 4.45 vs 8.13, 5XX 2.36 / 1.27 vs 3.58 / 2.24; per sweep it is lower on 49 of 63 (p < 0.001). **It needs no coverage:** 5XX A generic scan 2.88 vs our 13.57. Ours better on 5XX A exam (2.28 vs 3.79) and in the occlusion block 4XX E (7.07 vs 24.03: one occluded sweep 81.5 mm while it reports tracking OK). Both fail after a very large rearrangement (C with B's scan: 19.2 on half the sweeps vs our 40.9). **Its map, not its tracking, is the advantage:** relocalising every frame on its own (our task) keeps it ahead (5XX 2.33 vs 3.58, generic scan 2.76 vs 13.57; 52 of 63 sweeps). **Ours degrades gracefully, it does not:** under a synthetic occluder ours goes 4.43 → 5.28 (5XX B) with every sweep ≤ 8.5 mm; ORB-SLAM3 stays lower on average but fails on single sweeps by 13–132 mm while reporting tracking OK, in every mode (4.11) | 4.10, 4.11 |
| Model variants | Big head + clean labels adopted (lower p90 and rotation); viewpoint augmentation, full resolution, refined pose fit, multi-frame anchors: neutral or worse | 4.5 |

## 1.1 Claims and evidence

What the data support, and how strongly. **Strong:** several splits, large effects, rule fixed before the run. **Moderate:** one main split or a caveat that must be stated with it. **Not claimed:** mixed or missing evidence.

| # | claim | evidence | strength | state with it |
|---|---|---|---|---|
| 1 | One SCR network on every frame replaces odometry + anchors | all 7 splits: median equal to SCR + SIFT odometry (4XX 6.48 vs 6.54 mm), as smooth or smoother; rule fixed on 2XX | **strong** | |
| 2 | Smoother tracking than every alternative | step error 3XX 0.93 vs 1.09 (classical), 4XX 1.07 vs 1.28 mm; every split | **strong** | |
| 3 | Predicting room coordinates + geometric solver beats pose regression | anchors 3XX 1.8 vs 15.3 mm, 4XX 6.0 vs 49 mm; every split | **strong** | |
| 4 | Room-scan coverage decides the accuracy | covered frames 4.1 vs uncovered 13.4 mm; earlier sweeps added to the map (Polaris labels) 4XX A 5.6 → 2.0 mm; 20 s scans along the viewpoints match classical, 130 s off them do not; 5XX A, same sweeps: 2.28 vs 13.57 mm (96 vs 0 % covered), 10.95 with Polaris labels | **strong** | |
| 5 | SCR can use all room scans of the day despite moved objects; feature matching cannot | 4XX B–E: SCR 6.82 → 5.53, classical 4.90 → 13.93 mm with the same pooled scans | **strong** | pooling decided on test blocks; B confirmed it |
| 6 | The ultrasound images add nothing to the camera pose | 10 tests in two phases; Li et al. reproduced on its own data | **strong** (this setup) | |
| 7 | More accurate than classical where the scan covers the sweep viewpoints | 3XX 1.85 vs 3.1 mm, three seeds 1.85–2.12; 2XX 3.35 vs 4.2 | moderate | strict protocol (map before the sweeps): on par, 2.98 vs 3.0 |
| 8 | Better volume shape than classical | after a rigid fit, every split: 2XX 3.04 vs 3.98, 3XX 1.57 vs 2.47, strict 2.26 vs 2.59, 4XX 2.95 vs 3.34 mm | moderate | metric introduced after the 4XX gap was known; report the absolute error too |
| 9 | Real time | 0.25 s delay gives the offline result on every split; fully causal: same median, steps +20 %; 60–70 ms per frame | moderate | offline replay of recordings, not run live |
| 10 | Works without a tracker: the network builds its own training labels | 3XX 2.34 / 1.72 mm (Polaris labels 1.85 / 1.57, classical 3.11 / 2.47), three seeds 2.22–2.34; strict 2.94; 4XX shape 2.69 (better than classical, behind ORB-SLAM3 1.29); every frame mapped and tracked; each component needed (Table F); 5XX (third session, phantom) 2.28 mm with an exam-view scan, 0.4 mm behind Polaris labels (1.85), as in 3XX | **strong** for shape, moderate for absolute | camera calibration fitted with Polaris once per probe; 4XX absolute 7.92 vs 6.48 / 4.76; 2XX map failed (8.06); needs a scan along the exam views (4.9) |
| 11 | Rescan after major changes; the inlier count flags an outdated map | 5XX: old map 4.28 mm after a large change, 13.9–59 mm after a very large one or an emptied room; median inliers 23–450 vs ≥ 1126 for maps that work | moderate | one session; threshold not tuned |

**Not claimed** (and why):

- *Robust to the room changing after the scan:* with an outdated map SCR is better in 2 of 3 cases (2XX → 3XX 6.5 vs 10.4 mm, A → C 13.4 vs 80.1) and worse in one (A → B 14.0 vs 7.9); both are 2–7× worse than with a current scan. Rule: rescan after a change, keep the old scans in the map. 5XX: a large rearrangement is tolerated, a very large one is not (4.9).
- *Accurate from any room scan:* a scan that misses the exam views gives 11–14 mm (5XX A), even with Polaris labels.
- *Better than classical in new sessions with short room scans:* 4XX 5.45 vs 4.76 mm (1.15×).
- *As accurate without a tracker as with Polaris labels:* 3XX 2.34 vs 1.85 mm, 4XX 7.92 vs 6.48 (Tables F, G); the camera calibration still needs Polaris once.
- *Better than RGB-D SLAM, or the best shape of all systems:* ORB-SLAM3 RGB-D (no tracker either) is better, also like for like (map from the room scan only, then frozen): 49 of 63 sweeps, shape on every current split, and it needs no coverage (4.10).
- *More accurate than ORB-SLAM3 under occlusion:* it is lower on average also with an occluder; what holds is that ours degrades gracefully (worst sweep 8.5 mm at 60 %) while ORB-SLAM3 fails on single sweeps by 13–132 mm while reporting tracking OK (4.11; two blocks, one occluder).
- *One network trained end to end:* the system is one SCR network plus exact geometry (Kabsch, ICP, pose graph), by design (`note.md` 1).
- *Generalises to new rooms:* the network is trained per room, by design.
- *2 mm everywhere:* reached on the well-covered session only.

## 1.2 Overview tables

Seven tables cover every test: A every system at the US image, B single-image pose methods, C coverage (what decides SCR vs classical), D where the error sits (local, shape, placement), E one row per test with its verdict, F the system without a tracker and its ablations (3XX), G without a tracker on every split. 4XX mean = mean of A–E. Details are in the sections given. As figures: `tools/tables/table_A.png` … `table_F.png` and `tools/tables/overview_tables.pdf` (`python tools/draw_overview_tables.py`; numbers copied from here, edit both together).

**Table A. Every system at the US image** (median mm per sweep, mean over sweeps; 3.1, 4.6)

| system | 2XX val | 3XX | 3XX strict | 4XX A | B | C | D | E | **4XX mean** | step 3XX / 4XX |
|---|---|---|---|---|---|---|---|---|---|---|
| classical odometry only (SIFT VO, each segment starts at the true pose) | 37.0 | 9.4 | 9.8 | 15.1 | 11.3 | 8.9 | 12.7 | 12.9 | 12.2 | |
| SCR every 0.25 s + RPRNet odometry, pose graph | | 3.2 | | 5.4 | | | 9.9 | | | 1.51 / |
| SCR anchors + SIFT odometry, pose graph (hybrid) | 4.2 | 2.6 | | 5.0 | 5.7 | 5.9 | 9.6 | 6.5 | 6.54 | 1.08 / 1.29 |
| **classical anchors + SIFT odometry** (classical system) | 4.2 | 3.1 | 3.0 | **4.2** | **3.4** | 4.9 | **6.3** | **5.0** | **4.76** | 1.09 / 1.28 |
| classical system, map = all same-day room scans up to the block | | | | | 5.5 | 21.1 | 18.9 | 10.2 | | |
| one SCR network, raw | 3.59 | 2.03 | 3.12 | 5.21 | 5.82 | 5.76 | 9.57 | 6.12 | 6.50 | 1.67 / 1.82 |
| **one SCR network, 2 s smoothing (ours)** | **3.35** | **1.85** | **2.98** | 5.14 | 5.77 | 5.63 | 9.63 | 6.25 | 6.48 | **0.93 / 1.15** |
| **one SCR network, all same-day room scans up to the block (ours, final)** (B: A + B scans; C, D, E: A + B + C; A unchanged) | | | | 5.14 | 3.76 | **3.98** | 8.46 | 5.92 | 5.45 | / 1.07 |
| same, real time with 0.25 s delay (window 1 s) | 3.32 | 1.86 | 2.95 | 5.14 | 3.75 | **3.98** | 8.40 | 5.88 | 5.43 | 0.93 / 1.06 |
| same, causal: no delay (window 0.25 s) | 3.26 | 1.95 | 3.05 | 5.22 | 3.67 | **3.94** | 8.43 | 6.08 | 5.47 | 1.18 / 1.28 |

- Odometry alone drifts (9–15 mm); every working system needs an absolute pose per frame or per second.
- The single network equals the hybrid on every split: SIFT odometry adds nothing once SCR runs on every frame; learned odometry is worse.
- Against classical: better on 3XX and 2XX, equal under the strict protocol, 1.4× worse on 4XX with each block's own scans, 1.15× with all scans of the day (C better than classical); always the smoothest.
- The same pooled scans ruin classical (C 4.9 → 21.1 mm): the moved objects in the earlier scans give confident wrong SIFT matches.
- Real time costs nothing with a 0.25 s delay, and only smoothness (steps +20 %, equal to classical's) when fully causal.

**Table B. Pose from one image** (anchors: camera position median mm, rotation median, one frame per second; 4.1, 4.2)

| method | 2XX val | 3XX | 4XX mean | rotation 3XX / 4XX | frames solved |
|---|---|---|---|---|---|
| RPR anchor network (pose regression) | | 15.3 | 49.0 | | 3XX 93 %, 4XX 37–92 % |
| SCR, first recipe, PnP | 15.8 | | | | all |
| SCR v1 (fixed training), PnP | 5.1 | 2.5 | 11.1 | | all |
| SCR v1, Kabsch on depth | 3.4 | 2.0 | 6.4 | 0.19° / 0.56° | all |
| **SCR v2 (big head, clean labels), Kabsch** | **3.4** | **1.8** | 6.0 | **0.19°** / 0.49° | all |
| classical (SIFT to the room scan) | 5.2 | 2.6 | **5.3** | 0.34° / **0.38°** | all but A → C |

- The two big steps are training long enough (15.8 → 5.1) and using the measured depth at test time (PnP → Kabsch, 4XX 11.1 → 6.4); the head and labels mostly lower p90 and rotation.
- SCR is 8× more accurate than pose regression on both 3XX and 4XX.
- SCR vs classical follows the same pattern as Table A; on 4XX rotation is SCR's weak spot (0.49° vs 0.38°, about 0.2 mm at the US image per 0.1°).

**Table C. What decides SCR vs classical: room-scan coverage** (anchors in mm; US image where measured; 4.3, 4.4, 4.7)

| map (training data) → test | sweep viewpoints covered | SCR anchors | classical anchors | SCR / classical | SCR system | classical system |
|---|---|---|---|---|---|---|
| 3XX, both room scans | 93–96 % | **1.8** | 2.6 | 0.7 | **1.85** | 3.1 |
| 2XX val, both room scans | 75 % | **3.4** | 5.2 | 0.65 | **3.35** | 4.2 |
| 3XX strict, room-301 only (recorded before the sweeps) | fewer | 3.1 (v1) | **2.7** | 1.15 | 2.98 | 3.0 |
| 4XX, own room scans (40–90 s) | 0–14 % | 6.0 | **5.3** | 1.13 | 6.48 | **4.76** |
| A run-405…408, + run-401…404 (Polaris labels) | added views | **2.0** (from 5.6) | 3.7 (from 5.9) | 0.54 | **2.3** (hybrid) | 3.2 |
| D run-421, 423, 424, + run-418…420 (Polaris labels) | added views | **3.3** (from 8.6) | 4.7 (from 7.4) | 0.70 | **4.5** (hybrid) | 5.8 |
| B–E: all room scans of the day up to the block (objects moved between blocks) | more views, partly outdated | | B–E 16.5 (from 5.0; 76–99 % accepted) | | **B 3.76, C 3.98**, D 8.46, E 5.92 (from 5.77, 5.63, 9.63, 6.25) | 5.5, 21.1, 18.9, 10.2 (from 3.4, 4.9, 6.3, 5.0) |
| same, labelled with the system's own poses | added views, wrong labels | A 5.0 (from 5.3), D 7.9 (from 9.0) | | | | |
| 2XX map → 3XX (a few objects moved) | outdated | **6.5** | 10.4 | 0.63 | | |
| A map → B (small rearrangement) | outdated | 14.0 | **7.9** | 1.8 | | |
| A map → C (large rearrangement) | outdated | **13.4** | 80.1 (21 % accepted) | | | |

- The SCR / classical ratio follows coverage: below 1 when the map covers the sweeps, about 1.1 when it does not.
- Adding real, correctly labelled views fixes it and SCR gains more from them than classical (A 5.6 → 2.0 vs 5.9 → 3.7).
- Room scans of the same day help SCR too, although objects moved between the blocks (B–E mean 6.82 → 5.53 mm, no labels on sweeps), while they ruin classical (4.90 → 13.93 mm): the network learns what stays put, SIFT matches whatever it finds.
- Views that are added but labelled wrongly (self-labels), or synthesised badly (point-splat renders, Table E), do not help: the training views must be correct.

**Table D. Where the error sits** (`runs/shape-final.md`, 3D pages; mm at the US image; 3.2, 4.8)

| split | system | absolute | shape (after a rigid fit of each sweep) | absolute − shape (placement) | out-of-plane error over 8 / 30 rows | 3D-page pixel error |
|---|---|---|---|---|---|---|
| 2XX val | **one SCR network** | **3.36** | **3.04** | 0.32 | 0.47 / 1.09 | **3.8** |
| 2XX val | classical system | 4.22 | 3.98 | 0.24 | 0.75 / 1.42 | 5.1 |
| 2XX val | classical odometry only | 36.98 | 14.26 | 22.72 | 0.69 / 1.44 | 29.4 |
| 3XX | **one SCR network** | **1.85** | **1.57** | 0.28 | 0.37 / 0.62 | **2.0** |
| 3XX | classical system | 3.11 | 2.47 | 0.64 | 0.29 / 0.62 | 3.2 |
| 3XX | classical odometry only | 9.43 | 6.23 | 3.20 | 0.28 / 0.54 | 10.1 |
| 3XX strict | **one SCR network** | 2.95 | **2.26** | 0.69 | 0.42 / 0.69 | 3.2 |
| 3XX strict | classical system | **2.91** | 2.59 | 0.32 | 0.34 / 0.72 | 3.2 |
| 3XX strict | classical odometry only | 9.77 | 6.14 | 3.63 | 0.33 / 0.62 | 10.4 |
| 4XX mean | **one SCR network** | 6.49 | **3.17** | 3.32 | 0.39 / 0.74 | 7.1 |
| 4XX mean | classical system | **4.75** | 3.34 | 1.41 | 0.39 / 0.76 | **5.2** |
| 4XX mean | classical odometry only | 12.19 | 6.66 | 5.53 | 0.41 / 0.86 | 12.5 |
| 4XX pooled | **one SCR network, same-day scans (A–E)** | 5.45 | **2.95** | 2.50 | 0.38 / 0.69 | 6.0 |
| 4XX pooled | classical system, same-day scans (B–E) | 13.92 | 8.30 | 5.62 | 0.46 / 1.12 | 15.5 |

- Between nearby frames all three are the same (0.3–0.4 mm over 8 rows): local motion is solved by any of them.
- The volume shape of the single network is better than classical's on every split mean: 2XX 3.04 vs 3.98, 3XX 1.57 vs 2.47, 3XX strict 2.26 vs 2.59, 4XX 3.17 vs 3.34 (A 2.92 vs 3.10, B 2.66 vs 2.47, C 2.96 vs 3.36, D 3.16 vs 3.61, E 4.16 vs 4.15).
- The whole 4XX gap is placement: each sweep is shifted rigidly in the room (3.3 mm vs 1.4 for classical). That is an anchoring error, which matches the coverage finding of Table C.
- With the pooled scans, the single network's shape is better than classical's (own scans) on every 4XX split: A 2.92 vs 3.10, B 2.19 vs 2.47, C 2.55 vs 3.36, D 3.36 vs 3.61, E 3.75 vs 4.15; placement shrinks to 2.5 mm.

**Table E. Every test and its verdict** ("anchors" = camera position median, "US" = system at the US image, mm; rules fixed before each run on 2XX, or on 4XX A for coverage)

| area | test | measured on | result | verdict |
|---|---|---|---|---|
| training | fixed recipe, 15 → 120 epochs | 2XX anchors (PnP) | 15.8 → 5.1 | **adopted** |
| training | full resolution 720 × 1280 (30 epochs) | 2XX anchors | 6.3 → 7.3 | no |
| training | viewpoint augmentation (zoom, rotation) | 2XX anchors | 3.4 → 6.5 | no |
| training | big head + clean labels (v2) | 2XX p90, rotation | 8.7 → 7.3, 0.33° → 0.27° | **adopted** |
| training | frozen ImageNet encoder | 4XX A US | 5.14 → 5.24 | no |
| training | + rendered views (point splats) | 4XX A US | 5.14 → 4.98 | no (rule: ≥ 0.5 mm better) |
| training | frozen encoder + rendered views | 4XX A US | 5.14 → 5.51 | no |
| training | seeds 0 / 1 / 2 | 3XX US | 1.85 / 1.95 / 2.12 | noise ≈ 0.3 mm |
| training | 240 instead of 120 epochs | 4XX A US (fit) | 5.14 → 5.28 (fit 1.24 → 1.05 mm) | no |
| training | rendered views from real frames (full resolution) | 4XX A US | 5.14 → 4.94 | no (rule: ≥ 0.5 better) |
| training | confidence head (unweighted solver) | 4XX A US | 5.14 → 5.22 | neutral |
| pose | pose regression (RPR) instead of SCR | 3XX / 4XX anchors | 15.3 / 49.0 vs 1.8 / 6.0 | **SCR** |
| pose | Kabsch on measured depth instead of PnP | 2XX anchors | 5.1 → 3.4 | **adopted** |
| pose | refined pose fit (noise weights; reprojection + depth) | 2XX anchors | 3.4 → 4.7 / 3.6 | no |
| pose | inlier gate ≥ 400 | all splits | trims tails on D, E, A → C | kept |
| pose | multi-frame anchors (3 / 5 frames) | 2XX US (hybrid) | 4.2 → 4.4 / 4.5 | no |
| pose | confidence-weighted Kabsch (same checkpoint) | 4XX A US | 5.22 → 5.28 | no |
| time | SIFT odometry + pose graph vs one network | 4XX mean US | 6.54 vs 6.48 | **odometry dropped** |
| time | RPRNet (learned) odometry instead of SIFT | 3XX / A / D US | 0.3–0.6 mm worse | no |
| time | 2 s robust smoothing vs raw | 3XX US (step) | 2.03 (1.67) → 1.85 (0.93) | **adopted** |
| time | real time: 0.25 s delay / causal (window chosen on 2XX) | 3XX US (step) | 1.85 (0.93) → 1.86 (0.93) / 1.95 (1.18) | **real time works** |
| time | pose graph with zero-motion odometry | 3XX US | 2.0 → 4.9 | no |
| time | gate recovery (hybrid only) | run-404 US | 28.3 → 8.2 | kept for the hybrid |
| time | pose-graph anchor σ 11 / 5 / 3 mm | 2XX US | 4.4 / 4.4 / 4.5 | default kept |
| map | + earlier sweeps, Polaris labels | 4XX A / D anchors | 5.6 → 2.0 / 8.6 → 3.3 | works, needs Polaris |
| map | + same-day room scans (A, B scans for C, D, E) | 4XX C / D / E US | 5.63 / 9.63 / 6.25 → 3.98 / 8.46 / 5.92 | **adopted** (rule: mean ≥ 0.5 better; 7.17 → 6.12) |
| map | same for B (A + B scans), as confirmation | 4XX B US | 5.77 → 3.76 | confirmed |
| map | classical system with the same pooled map | 4XX B / C / D / E US | 3.4 / 4.9 / 6.3 / 5.0 → 5.5 / 21.1 / 18.9 / 10.2 | no: classical keeps its own scans |
| map | + earlier sweeps, labelled with own poses | 4XX A / D anchors | 5.3 → 5.0 / 9.0 → 7.9 | no |
| map | strict protocol (room-301 only) | 3XX run-315…317 US | 1.85 → 2.98 (classical 3.0) | report both |
| map | outdated map (previous session) | anchors | 2XX → 3XX 6.5; A → B 14.0; A → C 13.4 | re-scan per session |
| map | shorter room scans: first 20 / 40 s of each | 3XX US | 3.00 / 2.03 vs 1.85 (~60 s) | study: content over length |
| map | map without a tracker: the network + depth ICP build the room-scan poses (labels) | 3XX US / shape | 1.85 / 1.57 (Polaris labels) → 13.26 / 8.54 | works, not accurate |
| map | map aligned to Polaris on view points, not camera positions (evaluation) | 3XX US | 50.6 → 12.8 | fixed |
| map | joint refinement of network and map poses | 3XX map camera position | 8.4 → 8.9 | no |
| map | + pose graph over the room scan (depth ICP edges + network priors) | 3XX US / shape | 13.26 / 8.54 → 12.49 / 4.74 | **adopted** |
| map | pose-graph prior 10 / 30 mm | 3XX map scene points | 6.9 / 7.3 | default kept |
| map | + camera calibration from the room scan (one camera-frame transform, applied when tracking) | 3XX US / shape (with loops) | 11.49 / 4.08 → 2.34 / 1.72 | **adopted** |
| map | + loop closures in the pose graph | 3XX US / shape | 5.77 / 3.18 → 2.34 / 1.72 | **adopted** |
| map | pooled scans of the day (no tracker) | 4XX B–E US | 8.64 → 10.85 | no (each block's scans) |
| map | 3XX camera calibration reused in a new session | 4XX US / shape | 7.92 / 2.69 | placement open |
| US | U1 in-plane registration (ECC) | 2XX, 10 rows | 1.91 vs 1.55 for zero motion | no |
| US | U2 speckle decorrelation → distance | all | 0.27–0.43 mm, magnitude only | no |
| US | U3 per-patch speckle vs camera | 3XX, 4 rows | 0.78 vs camera 0.19 mm | no |
| US | Li et al. reproduced on its own data | their test set | 21.4 vs 22.8 mm published | reproduced |
| US | Li et al. on our sweeps | 3XX / A / D | zero-shot 129; fine-tuned 75–125; scratch = zero motion | no |

**Table F. Without a tracker: the final system and its ablations** (3XX; training labels from the map the network builds itself (`scr_map.py`), Polaris for evaluation only; one component removed per row; `runs/repro/`, `runs/repro/shape-3XX*.md`, `runs/shape-map-3XX.md`, `runs/shape-graph-3XX.md`; mm; 8)

| training labels from | map: scene points at 1 m | map: camera position | map: 1 s motion | US: absolute | US: shape | placement | out-of-plane 8 / 30 rows | step 8 rows |
|---|---|---|---|---|---|---|---|---|
| **map: seed + rounds + pose graph with loop closures + camera calibration (the system)** | **2.6** | **2.0** | **1.5** | **2.34** | **1.72** | 0.62 | 0.37 / 0.62 | **0.90** |
| the same, seeds 1 / 2 (mapping and training) | 2.7 / 2.7 | 2.0 / 1.9 | 1.5 / 1.4 | 2.22 / 2.25 (mean 2.27) | 1.75 / 1.70 (mean 1.72) | | | |
| − loop closures | 4.5 | 5.2 | 1.5 | 5.77 | 3.18 | 2.59 | 0.40 / 0.70 | 1.05 |
| − camera calibration | 6.4 | 10.4 | 3.4 | 11.49 | 4.08 | 7.41 | 0.48 / 1.18 | 1.06 |
| − loop closures − camera calibration (earlier code, `runs/map-3XX-graph`) | 6.9 | 11.6 | 3.4 | 12.49 | 4.74 | 7.75 | 0.46 / 1.24 | 1.14 |
| − pose graph − camera calibration: each frame localised on its own (earlier code, `runs/map-3XX`) | 9.0 | 15.3 | 7.2 | 13.26 | 8.54 | 4.72 | 0.46 / 1.14 | 1.39 |
| pose graph, priors 30 instead of 10 mm (map only, not trained) | 7.3 | 12.2 | 3.4 | – | – | – | – | – |
| Polaris (oracle map, upper bound) | – | – | – | 1.85 | 1.57 | 0.28 | 0.37 / 0.62 | 0.93 |
| classical system (its room-scan keyframes posed by Polaris) | – | – | – | 3.11 | 2.47 | 0.64 | 0.29 / 0.62 | – |
| classical odometry only (no map; segment start from Polaris) | – | – | – | 9.43 | 6.23 | 3.20 | 0.28 / 0.54 | – |

- Only the map rows use no tracker at any stage. The classical system needs no training labels, but its room-scan keyframes are posed by Polaris (`baselines/anchoring.py`): a tracker-mapped reference. A tracker-free classical baseline (an RGB-D SLAM map) is still missing.
- The network reproduces its labels (same network: 1.85 mm with Polaris labels, 12.5–13.3 mm with the first map labels), so the map decides the result.
- Every component is needed. The pose graph ties neighbouring frames (1 s motion 7.2 → 3.4 mm, shape 8.54 → 4.74); the camera calibration removes a fixed camera-frame offset (the hand–eye mismatch between the Polaris marker and the camera: 31.7 mm, 1.51°) and with it most of the absolute error (11.49 → 2.34); the loop closures remove the slow bending of the map (camera 5.2 → 2.0 mm, rotation 0.55 → 0.19°; US 5.77 → 2.34, shape 3.18 → 1.72).
- Without the calibration the shape suffers too (4.08 vs 1.72): a camera-frame rotation error moves the US image differently as the probe turns.
- A looser prior (30 mm) gives the same 1 s motion: the local error sits in the ICP edges, not the priors. Joint refinement of the network and the map poses (ACE0-style) made the map worse (camera 8.4 → 8.9 mm; Table E).
- The final system is 0.5 mm behind the oracle map (2.34 / 1.72 vs 1.85 / 1.57) and ahead of the Polaris-mapped classical system (3.11 / 2.47). The seed spread (2.22–2.34) is smaller than with Polaris labels (1.85–2.12).

**Table G. Without a tracker on every split** (US image, mm; 2 s smoothing; step over 8 rows in brackets; map = scene points at 1 m / camera position / 1 s motion after one alignment; `runs/map-*`, `runs/track-v2map-*`, `runs/shape-v2map-*.md`, `runs/shape-trackerfree-4XX-samerows.md`, `runs/repro/`)

| split | camera calibration | map | **absolute** | **shape** | Polaris labels: absolute / shape | classical: absolute / shape |
|---|---|---|---|---|---|---|
| 3XX | fitted on its room scan | 2.6 / 2.0 / 1.5 | **2.34** (0.90) | **1.72** | 1.85 / 1.57 | 3.11 / 2.47 |
| 3XX strict (map room-301 only, run-315…317) | fitted on room-301 | 2.6 / 2.2 / 1.9 | **2.94** (1.17) | 2.18 | 2.98 / 2.26 | 3.0 / 2.59 |
| 2XX validation (run-205, 211) | 3XX | 6.7 / 8.3 / 3.6 (p90 31.2) | 8.06 (2.57) | 6.93 | 3.35 / 3.04 | 4.2 / 3.98 |
| 4XX A | 3XX | 3.9 / 4.8 / 2.4 | 5.04 | 2.94 | 5.14 / 2.92 | 4.2 / 3.10 |
| 4XX B | 3XX | 3.1 / 3.0 / 1.4 | 6.55 | 2.40 | 5.77 / 2.66 | 3.4 / 2.47 |
| 4XX C | 3XX | 3.5 / 3.4 / 1.7 | 9.40 | 2.05 | 5.63 / 2.96 | 4.9 / 3.36 |
| 4XX D (C's map) | 3XX | C's | 11.54 | 3.10 | 9.63 / 3.16 | 6.3 / 3.61 |
| 4XX E (C's map) | 3XX | C's | 7.07 | 2.98 | 6.25 / 4.16 | 5.0 / 4.15 |
| 4XX mean | | | 7.92 | **2.69** | 6.48 / 3.17 | 4.76 / 3.34 |
| 4XX pooled scans of the day (B / C / D / E) | 3XX | 4.0–4.3 / 5.7–5.9 / 1.9 | 8.08 / 10.69 / 14.00 / 10.62 | 2.53 / 2.21 / 3.98 / 3.15 | 3.76 / 3.98 / 8.46 / 5.92 | worse (B–E 13.93) |

- 4XX: the maps are as good as 3XX's (scene points 3.1–3.9 mm), and the shape is better than classical's on every block (same rows: 2.73 vs 3.34; ORB-SLAM3 1.29, 4.10), but the placement is weak (C, D). Calibrations fitted on the 4XX scans differ from 3XX's in rotation (1.9–2.05° vs 1.51°): either the calibration does not transfer, or the map's placement. Test: Section 8, task 1.
- Pooled scans of the day are worse without a tracker (the map has to join scans of a room whose objects moved); with Polaris labels pooling helped. Without a tracker: each block's own scans.
- 2XX fails: round 2 made the map worse (camera 18.6 → 22.1 mm), the per-scan calibrations disagree (0.93° vs 1.89°), and the 1 s motion has a 31 mm p90: some frames were joined wrongly and the pose graph did not fix them. Its scans are the longest (3 min, 5,366 frames). Not yet understood.
- Real time (4XX, `--lags 0.25 0`): with a 0.25 s delay the error equals the offline result on every block (A 5.01, B 6.54, C 9.41, D 11.61, E 7.05 mm, 1 s window), fully causal the median rises by at most 0.2 mm and the step over 8 rows by 0.3–0.4 mm. 3XX: 2.34 (0.90) with the delay, 2.42 (1.13) causal.
- 3D pages (pixel error over the compounded volumes, `runs/repro/volume3d/`, `runs/volume3d-trackerfree/`): 3XX 2.5 (classical 3.2, odometry only 10.1), strict 3.3, 4XX A 5.7 / B 6.4 / C 9.9 / D 12.2 / E 7.5 (classical 4.4 / 3.7 / 5.3 / 7.2 / 5.2).

**Conclusions from the seven tables**

1. **Geometry beats regression.** Predicting room coordinates and solving the pose on the measured depth is what works (Table B); every learned shortcut (pose regression, learned odometry, US-only networks) is worse or no better than zero motion (Tables A, E).
2. **One network is enough.** With SCR on every frame and smoothing, odometry adds nothing (Table A), and the shape and local accuracy are classical-grade or better (Table D).
3. **Coverage is the limit.** SCR wins where the room scan covers the sweep viewpoints and loses when it does not (Table C). The 4XX loss is a rigid placement offset, not a worse volume: the shape is better than classical's on every split (Table D).
4. **Only real, correctly placed training views close the gap.** Polaris-labelled sweeps do (A 5.6 → 2.0), and so do more room scans of the same day (B–E 6.82 → 5.53); self-labels, frozen features, more epochs and point-splat renders do not (Tables C, E). Next steps: longer room scans, or a realistic renderer.
5. **SCR can use partly outdated data, classical cannot.** Room scans from earlier in the day, with objects moved since, improve SCR and ruin classical (B–E 4.90 → 13.93 mm, Tables A, C). More scanning always helps SCR.
6. **It runs in real time:** a 0.25 s delay gives the offline accuracy; fully causal only adds some jitter (Table A).
7. **The US images carry no usable pose information** beyond what the camera gives (Table E, US rows).
8. **No tracker is needed.** The network reproduces its labels, so the map decides the result. With a pose graph (depth-ICP edges and loop closures) and the probe's camera calibration the map is good enough: 3XX 2.34 mm at the US image, shape 1.72 mm, 0.5 mm behind the oracle map and ahead of the Polaris-mapped classical system (3.11 / 2.47; Table F). Each component is needed (without loops 5.77, without calibration 11.49). In new sessions the shape stays better than classical's (4XX 2.69 vs 3.34), the placement does not (Table G). ORB-SLAM3 RGB-D, also without a tracker, is better in both (4XX 3.55 / 1.29; 4.10).

## 2. Setup

**Task.** A probe-mounted RGB-D camera gives the pose of every ultrasound image, with nothing outside the probe during the exam. Target: ~2 mm at the US image (the elevational beam width), ~16 cm from the camera (1° ≈ 1.6 mm at the image bottom).

### 2.1 Data

**Sensors and ground truth.**

- **Camera:** RealSense D435i on the probe; colour 1280 × 720 at ~30 Hz, depth aligned to colour (uint16 mm, reliable 0.1–3 m, noise growing with distance², missing on dark or shiny surfaces and closer than ~0.2 m).
- **Ultrasound:** screen grab of the scanner (depth 9 cm, gain 48 %, 19 frames/s), cropped to 640 × 480 at 0.2295 × 0.2213 mm/px; ~25 grabs/s with ~25 % repeated frames (flagged); the fan fades at depth and at the sides.
- **Ground truth:** NDI Polaris marker on the probe (~0.1–0.25 mm, 20 Hz, interpolated to the camera frames; clock offset measured against the camera gyro and corrected). Camera pose = marker pose × hand-eye (board-corner error 3.5 mm); US image pose = camera pose × hand-eye⁻¹ × US calibration (N-wire phantom).
- **Two kinds of recording:** *room scans*, the probe camera moved around the room without ultrasound (the only training data of SCR); *sweeps*, ultrasound scans of a subject (only evaluated). One `frames.csv` per recording matches all streams; frames without a marker pose, or with the probe in the air, are skipped.

**Collections** (one per recording day; coverage = share of evaluated sweep frames with a room-scan camera pose within 30 mm and 10°, from `runs/coverage_error.md`):

| collection | date | room scans | sweeps | what it is | coverage | role |
|---|---|---|---|---|---|---|
| 1XX | 8 Oct | room-101, 102 | run-101…112 | depth wrong (cable in front of the sensor), marker often lost | – | not used |
| 2XX | 9 Oct | room-201, 202: 3.0 min, 5,366 frames | run-201…212; evaluated: run-205, run-211 | first clean session, subject 1 | 75 % | **validation**: every setting is chosen here |
| 3XX | 9 Oct | room-301, 302: 2.0 min, 3,356 frames | run-313…317 (5) | same room later that day, a few small objects moved; room-302 recorded after the sweeps; subject 1 | 96 % | test (strict variant: room-301 only, sweeps run-315…317) |
| 4XX | 14 Oct | room-401…406 (6 scans) | run-401…428 without 417, 422 (26) | new session in five blocks A–E (below): room changes, a second subject, occlusion | 0–14 % | test (block A also validation for coverage questions) |

**4XX blocks** (recorded in this order on 14 Oct):

| block | room scans | sweeps | subject | condition | coverage | pooled training scans |
|---|---|---|---|---|---|---|
| A | room-401 (90 s), 402 (40 s): 3,893 frames | run-401…408 (8) | 1 | new session; scans held low, away from the sweep viewpoints | 5 % | – (first block) |
| B | room-403, 404 (40 s each): 2,381 frames | run-409…412 (4) | 1 | small rearrangement (box, bottles, a mouse) | 12 % | A + B: 6,274 frames |
| C | room-405, 406 (40 s each): 2,397 frames | run-413…416 (4) | 1 | large rearrangement (objects removed and added) | 0 % | A + B + C: 8,671 frames |
| D | C's scans | run-418…421, 423, 424 (6) | **2** | second subject; an arm briefly in view (run-419…421) | 0 % | A + B + C |
| E | C's scans | run-425…428 (4) | **2** | occlusion: an arm across the view 22–29 % of the time (run-425, 426) | 14 % | A + B + C |

In all: 2 + 5 + 26 = 33 evaluated sweeps; 4XX sweeps are slower than 2XX (6–18 mm/s). Quirks: `record_config.json` in 3XX carries old run names (trust the folder); in 4XX run-427 was run-422 and run-428 was run-417. Details: `note.md` 3.

### 2.2 Protocol and final model

**Protocol.** One model per session, trained on its room scans only (Polaris poses), tested on its sweeps. Anchor accuracy: camera position / rotation error against Polaris, one frame per second, mean of per-sweep medians / p90. System accuracy: **median error at the US image** (5 points via the US calibration) per sweep, mean over sweeps; **step-to-step error** = mean change of the error vector over 8 rows (0.27 s). Rules for adopting a change are fixed before the run and decided on 2XX; tests only report. Run-to-run noise: ~1 mm on 2XX (2 sweeps), ~0.3 mm on 3XX (seeds).

**Final model (v2, `scr_anchor.py train --head big --label-max-depth 2000 --drop-depth-edges`).**

| | first SCR (`rgbd-us/scr.py`) | **v2** |
|---|---|---|
| network | RGB 3 × 360 × 640 → EfficientNet-B0 (ImageNet), stride-8 (40 ch) + upsampled stride-16 (112 ch) features → 1×1 head 152→256→256→256→3 (0.17 M) → room coordinate per cell, 45 × 80 | same encoder; **big head**: 1×1 152→512, 4 residual blocks (512), 512→3 (2.18 M), fp32 |
| labels | room-scan depth at each cell centre, back-projected with the Polaris pose | same, **depth 0.1–2 m only, none on depth edges** |
| training | every 2nd frame, Huber (50 mm knee), OneCycle, 15 epochs, fp16 head | **every frame, 3D distance, flat lr 60 % then cosine, 120 epochs**; AdamW, head lr 1e-3, encoder 1e-4, batch 8; 20–50 min on an RTX A4500 |
| pose | PnP-RANSAC, 10 px | **Kabsch RANSAC on the measured depth**: 256 hypotheses, 20 mm, cells < 2 m, 3 refits; frame used only with ≥ 400 inliers |

## 3. Final system

### 3.1 One network on every frame (`scr_anchor.py track`, `runs/track-*`)

SCR + Kabsch on every 2nd usable row (15 Hz), no odometry, no Polaris start pose; a robust local fit over time (window chosen on 2XX by the rule "lowest median with a step error at most SCR + SIFT's": **2 s**; offline, as the pose graph). Median error at the US image (mm), step-to-step error in brackets.

| split | **SCR alone, smoothed 2 s** | SCR alone, raw | SCR anchors + SIFT odometry, pose graph | classical anchors + SIFT odometry |
|---|---|---|---|---|
| 2XX val | **3.35** (1.20) | 3.59 (2.72) | 4.2 (2.22) | 4.2 (2.27) |
| 3XX | **1.85** (0.93) | 2.03 (1.67) | 2.6 (1.08) | 3.1 (1.09) |
| 4XX A | 5.14 (0.99) | 5.21 (1.75) | 5.0 (1.10) | **4.2** (1.13) |
| 4XX B | 5.77 (0.92) | 5.82 (1.76) | 5.7 (1.33) | **3.4** (1.32) |
| 4XX C | 5.63 (0.82) | 5.76 (1.48) | 5.9 (1.17) | **4.9** (1.19) |
| 4XX D | 9.63 (1.34) | 9.57 (1.92) | 9.6 (1.18) | **6.3** (1.19) |
| 4XX E | 6.25 (1.68) | 6.12 (2.19) | 6.5 (1.65) | **5.0** (1.57) |
| 3XX, seeds 1 / 2 | 1.95 (0.92) / 2.12 (0.93) | 2.11 / 2.20 | 2.7 / 2.7 (v1) | |
| 3XX strict (map room-301 only, run-315…317) | 2.98 (1.18) | 3.12 (1.94) | | 3.0 (1.34) |

- One network is enough: the rule (median equal to SCR + SIFT, step within 20 %) is met on all six test splits; same or better median, as smooth or smoother (2-row step 0.30–0.73 mm). 3XX: every sweep 1.4–2.1 mm; three seeds 1.85, 1.95, 2.12 (spread 0.27 mm), all below classical (3.1).
- Strict protocol: 2.98 vs 3.0 mm for classical (per sweep 3.7 / 2.4 / 2.9 vs 2.9 / 2.2 / 3.7), smoother (1.18 vs 1.34): on par, as the anchors were (4.7).
- 4XX: on average 6.48 mm vs 4.76 for classical (1.4×). Smoothing cannot remove a wrong-but-consistent error (D run-420, 421; E, where 6 % of the frames fail the gate, raw 6.12 vs smoothed 6.25): coverage decides 4XX.
- Offline smoothing (the 2 s window sees 1 s ahead); real-time versions in 3.3.

### 3.2 3D pages (`runs/volume3d/index.html`)

One page per sweep (`runs/volume3d/<split>/<run>.html`, open in a browser): the US volume compounded with the true poses and with the single network, the classical system and classical odometry only; mean pixel error over the compounded US images (the rgbd-us headline metric). The index lists every sweep.

| split | one SCR network | classical system | classical odometry only |
|---|---|---|---|
| 3XX | **2.0** | 3.2 | 10.1 |
| 4XX A | 5.4 | **4.4** | 14.5 |
| 4XX B | 5.8 | **3.7** | 11.1 |
| 4XX C | 6.6 | **5.3** | 9.8 |
| 4XX D | 10.4 | **7.2** | 13.1 |
| 4XX E | 7.1 | **5.2** | 13.8 |
| 2XX val | **3.8** | 5.1 | 29.4 |
| 3XX strict | 3.2 | 3.2 | 10.4 |
| 4XX B / C / D / E, same-day scans pooled (both systems) | 4.0 / 4.7 / 9.2 / 6.5 | 5.8 / 19.9 / 22.0 / 14.2 | 11.1 / 9.8 / 13.1 / 13.8 |

Same ranking as 3.1. Earlier pages of the hybrid system (SCR anchors + SIFT odometry; 3XX 2.7 vs 3.2 mm for classical, 4XX 5.3–10.5 vs 3.7–7.2) are in git commit 50ef6f5 (`runs/volume3d-final`).

### 3.3 Real time (`track --lags`, same cached poses)

The smoother sees only the poses known by t + delay (window of the last W s, extrapolated linearly to t). Rule fixed before the runs: per delay, the window with the lowest 2XX median: no delay 0.25 s, 0.25 s delay 1 s, 0.5 s delay 2 s. US image median (step over 8 rows); B–E with the pooled-scan models:

| split | offline 2 s | 0.25 s delay, window 1 s | causal, window 0.25 s | raw |
|---|---|---|---|---|
| 2XX val | 3.35 (1.20) | 3.32 (1.30) | 3.26 (1.82) | 3.59 (2.72) |
| 3XX | 1.85 (0.93) | 1.86 (0.93) | 1.95 (1.18) | 2.03 (1.67) |
| 3XX strict | 2.98 (1.18) | 2.95 (1.17) | 3.05 (1.42) | 3.12 (1.94) |
| 4XX A / B / C / D / E | 5.14 / 3.76 / 3.98 / 8.46 / 5.92 | 5.14 / 3.75 / 3.98 / 8.40 / 5.88 | 5.22 / 3.67 / 3.94 / 8.43 / 6.08 | 5.21 / 3.80 / 4.03 / 8.44 / 5.92 |
| 4XX mean | 5.45 (1.07) | **5.43 (1.06)** | 5.47 (1.28) | 5.48 (1.77) |

A 0.25 s delay gives the offline result on every split. Without delay the median is unchanged and the steps grow ~20 %, to the level of the classical system (3XX 1.09, 4XX 1.28). A 0.5 s delay (window 2 s) is no better than 0.25 s (4XX 5.42 (1.16)).

## 4. Studies behind the design

### 4.1 Training fixes (2XX validation, PnP unless noted)

| model | anchors (median / p90) | training-frame pose |
|---|---|---|
| first SCR recipe | 15.8 / 31.3 | 13.2 mm |
| fixed recipe, 30 / 60 / 120 epochs | 6.3 / 5.4 / **5.1** | 5.6 / 4.0 / 2.7 mm |
| 120 epochs + **Kabsch** (depth at test time) | **3.4 / 8.7**, 0.33° | |
| full resolution 720 × 1280 (30 epochs) | 7.3 / 14.5 | 6.6 mm |
| classical anchors | 5.2 / 11.9, 0.33° | |

Beyond ~60 epochs validation stops improving while the fit keeps improving: the limit becomes generalisation. The coordinate error (~12 mm) is scatter that RANSAC averages into 2–5 mm poses.

### 4.2 Anchor accuracy (Kabsch, one frame per second)

| split | **SCR v2** | SCR v1 (small head) | SCR v1 + PnP | classical anchors | RPR anchor network |
|---|---|---|---|---|---|
| 3XX | **1.8 / 3.4, 0.19°** | 2.0 / 3.3, 0.19° | 2.5 / 5.4 | 2.6 / 6.9, 0.34° | 15.3 (93 %) |
| 4XX A | 5.4 / 8.9, 0.45° | 5.9 / 10.1, 0.48° | 9.9 / 17.6 | **5.3 / 10.1, 0.48°** | 40.3 (73 %) |
| 4XX B | 5.6 / 8.0, 0.35° | 5.9 / 9.2, 0.40° | 8.6 / 17.8 | **3.2 / 5.0, 0.25°** | 25.4 (92 %) |
| 4XX C | **4.8 / 9.9**, 0.59° | 5.2 / 10.1, 0.74° | 11.2 / 17.0 | 5.9 / 11.1, 0.39° | 67.0 (66 %) |
| 4XX D | 8.6 / 14.5, 0.64° | 9.3 / 18.9, 0.73° | 15.4 / 29.2 | **7.1 / 18.3, 0.41°** | 54.5 (58 %) |
| 4XX E | 5.7 / 9.7, 0.40° | 5.9 / 13.9, 0.46° | 10.2 / 20.5 | **5.2 / 8.5, 0.35°** | 57.9 (37 %) |

Seeds (v1): 3XX 1.9–2.2 mm over 3 seeds, 4XX A 5.8–5.9 mm. Rotation is SCR's weak spot on 4XX, and it dominates the error at the US image there.

### 4.3 Coverage and map extension

- **Coverage** (a room-scan pose within 30 mm and 10°): covered frames 4.1 mm, uncovered 13.4 mm (all splits pooled, v1 + PnP); 4XX A grows from 8.1 to 13.9 mm as the nearest room-scan pose goes from < 30 to 60–100 mm.
- **Map + earlier sweeps of the same block (Polaris labels)**, tested on the later sweeps (anchors; US image with the pose graph):

| block, test sweeps | map | SCR anchors | classical anchors | SCR system | classical system |
|---|---|---|---|---|---|
| A, run-405…408 | room scans | 5.6, 0.47° | 5.9, 0.48° | 5.0 | **4.5** |
| A | + run-401…404 (one sweep gives most of it) | **2.0 / 4.6, 0.20°** | 3.7 / 7.0, 0.36° | **2.3** | 3.2 |
| D, run-421, 423, 424 | C's room scans | 8.6, 0.76° | 7.4, 0.46° | 10.2 | **7.2** |
| D | + run-418…420 | **3.3 / 7.7, 0.27°** | 4.7 / 14.6, 0.35° | **4.5** | 5.8 |

- **Same, labelled with the system's own poses (no Polaris):** A 5.3 → 5.0, D 9.0 → 7.9 mm (Polaris labels: 1.9, 3.1). The network learns the label errors (5–14 mm); map extension is only as good as the poses of the added views.
- **Room scans of the same day pooled** (`v2pool-4XXC`: room-401…406, 8,671 frames, all recorded before the C sweeps; US image, 2 s smoothing): C 5.63 → **3.98**, D 9.63 → 8.46, E 6.25 → 5.92 mm (step 0.79 / 1.17 / 1.56). The rule fixed before the run (mean over C, D, E ≥ 0.5 mm better) is met: 7.17 → 6.12. C is now better than the classical system (4.9), D and E still worse (6.3, 5.0). Objects moved between A, B and C, yet the static parts of the room gain views. Confirmed on B (`v2pool-4XXB`: room-401…404, 6,274 frames): 5.77 → **3.76** mm (classical 3.4). **Classical with the same pooled maps** (`sys-classical-pool-4XX*`) gets much worse: B 3.4 → 5.5, C 4.9 → 21.1, D 6.3 → 18.9, E 5.0 → 10.2 mm; its anchors fall to 76–84 % accepted and 17–23 mm median on C–E. SIFT matches the moved objects of the earlier scans with consistent geometry; the network averages them out against the static room, and RANSAC rejects the rest. Shape with pooled scans (single network): A 2.92, B 2.19, C 2.55, D 3.36, E 3.75, mean 2.95 vs 3.34 for classical (own scans).
- **Room-scan length** (`v2-3XX-scan20`, `-scan40`: only the first 20 / 40 s of room-301 and room-302, 1,198 / 2,289 of 3,356 frames; US image, 2 s): 3.00 (1.03) / 2.03 (0.94) vs 1.85 (0.93) mm with the full ~60 s each. Even 20 s per scan matches classical (3.1); beyond 40 s the gain is small. On 4XX A, 130 s of scans give 5.14 mm: what decides is whether the scans pass the sweep viewpoints, not their length.

### 4.4 Outdated room scans (map of one session, sweeps of a later one; anchors)

| map → sweeps | SCR + Kabsch | SCR + PnP | classical | RPR |
|---|---|---|---|---|
| 2XX → 3XX | **6.5 / 11.8** | 21.2 / 47.8 | 10.4 / 20.3 | 39.8 |
| A → B (small change) | 14.0 / 25.4 | 31.7 / 47.3 | **7.9 / 12.9** | 81.6 |
| A → C (large change) | **13.4** / 113.0 (gated: 8.2 / 16.6, 49 % kept) | 47.4 / 65.2 | 80.1 (21 % accepted) | 51.8 |

### 4.5 Model and solver variants (2XX validation decides)

| variant | result | decision |
|---|---|---|
| big head (2.18 M) + clean labels | median same, p90 8.7 → 7.3 / 9.4 → 6.9, rotation 0.33 → 0.27° / 0.37 → 0.28° (2 seeds); every test split slightly better (4.2) | **adopted (v2)** |
| viewpoint augmentation (zoom 0.67–1.5, ±15°) | 2XX 3.4 → 6.5 mm; 4XX A 5.9 → 5.1 (noise) | not adopted |
| refined pose fit (depth-noise weights; joint reprojection + depth) | 3.4 → 4.7 / 3.6 mm | not adopted |
| multi-frame anchors (3, 5 frames pooled via odometry) | US image 4.2 → 4.4 / 4.5 mm | not adopted |
| inlier gate ≥ 400 | unchanged on unchanged rooms; trims tails on D, E, A → C; no effect on the system | kept (chosen after seeing the tests: report ungated too) |
| gate recovery (accept again after 3 agreeing rejected anchors) | fixed run-404 in the hybrid system (28.3 → 8.2 mm) | kept for the hybrid system |
| pose-graph anchor σ (11 / 5 / 3 mm) | 4.4 / 4.4 / 4.5 mm | default kept |

**Training strategies against the coverage gap** (29 Oct; 4XX A as validation because 2XX is 75 % covered; rule fixed in advance: adopt if the single-network system on 4XX A is ≥ 0.5 mm better than v2, about twice the seed spread). US image, 2 s smoothing (step in brackets); fit = pose of training frames:

| model on 4XX A | US image | fit | decision |
|---|---|---|---|
| v2 (reference) | 5.14 (0.99) | 1.2 mm / 0.12° | |
| frozen ImageNet encoder, head only (`--freeze-encoder`) | 5.24 (0.97) | 3.7 mm / 0.23° | not adopted |
| + 0.5 rendered views per frame (`--render-views 0.5`: 1,946 views splatted from a 5 mm point cloud of the room scan, camera moved ≤ 150 mm, turned ≤ 20°) | 4.98 (0.98) | 1.6 mm / 0.13° | not adopted (−0.16 mm, within noise) |
| both | 5.51 (0.95) | 4.2 mm / 0.27° | not adopted |
| 240 instead of 120 epochs | 5.28 (0.99) | 1.05 mm / 0.08° | not adopted: fits the scan better, generalises no better |
| + 0.5 rendered views per frame from the 3 nearest real frames at full resolution (`--render-source frames`, 1,946 views, real texture) | 4.94 (0.97) | 1.6 mm / 0.12° | not adopted (−0.20 mm) |
| confidence head (`--confidence`), unweighted / confidence-weighted Kabsch (`track --weighted`) | 5.22 (1.00) / 5.28 (1.11) | 1.3 mm / 0.12° | not adopted |

Frozen features fit the room worse and do not generalise better. Rendered views help slightly, but the point-splat renders are blocky with see-through holes (`runs/v2rv-4XXA/render_preview.jpg`): a large appearance gap to real images. Renders from the nearest real frames keep the real texture (`runs/v2rvf-4XXA/render_preview.jpg`) and give the same small gain (−0.20 mm): the renderer was not the limit. Both kinds of synthesis help a little and consistently, but far less than real views (pooled scans: B–E −1.3 mm); coverage is not bought by synthesis. The confidence head learns the error on the training frames, where it is small and uniform, so it does not flag the cells that fail on new viewpoints; weighting does not help.

### 4.6 Without SIFT odometry (`runs/sys-learned-*`)

Median at the US image (step in brackets). SCR every 0.25 s with RPRNet odometry (learned) and a pose graph: 3XX 3.2 (1.51), A 5.4 (1.19), D 9.9 (1.21), i.e. 0.3–0.6 mm worse than SCR + SIFT; with anchors every 1 s RPRNet drifts too much (3XX 5.0). SCR every 0.25 s alone, raw: 2.0 (1.69), 5.2 (1.81), 9.7 (1.88); a pose graph with zero-motion odometry hurts it (3XX 4.9). Hence the robust smoother of 3.1.

### 4.7 Strict protocol for 3XX (map recorded before the sweeps)

room-301 was recorded between run-314 and run-315, room-302 after all sweeps. Map on room-301 only, test run-315…317 (anchors; classical system at the US image):

| map | SCR anchors (v1) | classical anchors | classical system |
|---|---|---|---|
| room-301 + room-302 | **1.8**, 0.20° | 2.5, 0.29° | 2.9 |
| room-301 only (strict) | 3.1 / 6.1, **0.26°** | **2.7 / 6.1**, 0.32° | 3.0 |

SCR loses more from the shorter map (coverage again). The single-network system under this protocol (`v2-3XX-room301`, `track-3XX-room301`): 2.98 mm at the US image vs 3.0 for the classical system, on par (3.1).

### 4.8 Shape of the reconstruction (`runs/shape-final.md`, single network vs classical)

Error at the US image after the best rigid fit of each whole sweep (the volume's distortion, without its placement in the room), absolute in brackets. Single network: 2XX **3.04** (3.36); 3XX **1.57** (1.85); 3XX strict **2.26** (2.95); 4XX A 2.92, B 2.66, C 2.96, D 3.16, E 4.16, mean **3.17** (6.49). Classical system: 2XX 3.98 (4.22); 3XX 2.47 (3.11); 3XX strict 2.59 (2.91); 4XX 3.10, 2.47, 3.36, 3.61, 4.15, mean 3.34 (4.75). Odometry only: 2XX 14.26, 3XX 6.23, 3XX strict 6.14, 4XX 6.66. With all same-day room scans (final models): 4XX A 2.92, B 2.19, C 2.55, D 3.36, E 3.75, mean **2.95**, better than classical on every split. The single network's 4XX error is a rigid offset of each whole sweep; its shape is as good as classical's or better (Table D). The earlier hybrid (SCR anchors + SIFT) gave 3XX 2.1, 4XX 3.5. Caveat: the metric was introduced after the 4XX gap was known, so report it next to the absolute error.

### 4.9 Third session: coverage, map quality and scene changes (5XX, 5 Nov; no tracker)

Same room as 2XX–4XX, sweeps on a phantom. Each block has a generic room scan and a scan along the four exam views (V1–V4), so the same sweeps are tracked with two maps; later blocks are also tracked with an earlier block's map. Every map by `scr_map.py`, probe calibration from 3XX, nothing tuned on 5XX. **Reporting rule (fixed 6 Nov, before the analysis):** the exam-view scan is the protocol and gives each block's headline number, also where the generic scan happened to do better (B); the generic scan is a controlled test of a scan that misses the exam views. US image, smoothed 1 s (`runs/track-v2map-5XX*/scr_track.md`); shape after a rigid fit per sweep (`runs/shape-5XX.md`, `runs/shape-5XX-extra.md`); coverage = share of sweep frames with a room-scan pose within 30 mm and 10°, mean over the block's sweeps (rgbd-us `tools/check_coverage.py`); map camera = the self-made map against Polaris after one alignment; inliers = median Kabsch inliers over all tracked frames.

| block (sweeps) | map from | coverage | map camera mm | absolute | shape | inliers |
|---|---|---|---|---|---|---|
| A reference (8) | **room-502 exam views** | 96 % | 2.7 | **2.28** | 1.90 | 1818 |
| A | room-503 exam views, after the sweeps | – | 2.0 | 2.50 | 1.96 | 1732 |
| A | room-501 generic | 0 % | 6.5 | 13.57 | 3.79 | 1456 |
| B large rearrangement (8) | **room-505 exam views** | 75 % | 2.4 | **4.43** | 2.81 | 1846 |
| B | room-504 generic | 93 % | 2.2 | 3.36 | 2.46 | 1889 |
| C very large rearrangement (8) | **room-507 exam views** | 96 % | 2.2 | **3.11** | 1.76 | 2213 |
| C | room-506 generic | 78 % | 5.2 | 6.35 | 1.76 | 2166 |
| D people moving (4) | **C's room-507** | 98 % | 2.2 | **2.24** | 1.70 | 1823 |
| D | C's room-506 | 100 % | 5.2 | 5.07 | 1.28 | 1857 |
| E empty room (4) | **room-509 exam views** | 92 % | 4.3 | **5.85** | 3.04 | 1371 |
| E | room-508 generic | 97 % | 10.9 | 13.03 | 2.83 | 1439 |
| B, outdated map | A's room-502 | 91 % | – | 4.28 | 3.00 | 1126 |
| C, outdated map | A's room-502 | 84 % | – | 59.4 (21 % of frames posed) | 47.7 | 23 |
| C, outdated map | B's room-504 | 94 % | – | 40.9 (96 % posed) | 29.2 | 102 |
| E, outdated map | C's room-507 | 96 % | – | 13.9 (p90 46.6) | 14.6 | 450 |

Block A in detail (same 8 sweeps; `runs/track-v2-5XXA-*` = Polaris labels, `runs/track-v2map-5XXA-both`, `-exam-e20/40/80`):

| 5XX A | absolute | shape | reading |
|---|---|---|---|
| exam-view scan, Polaris labels (oracle) | **1.85** | 1.67 | upper bound |
| exam-view scan, our map | 2.28 | 1.90 | removing the tracker costs 0.4 mm (3XX: 1.85 → 2.34) |
| generic scan, Polaris labels (oracle) | 10.95 | 3.93 | coverage costs ~9 mm even with perfect labels |
| generic scan, our map | 13.57 | 3.79 | the self-made map adds 2.6 mm |
| both scans in one map (`map-5XXA-both`: camera 3.4 mm) | 3.15 | 1.81 | the generic footage makes the map worse (2.7 → 3.4 mm camera) |
| exam-view scan, 20 / 40 / 80 / 120 epochs | 2.53 / 2.34 / 2.37 / 2.28 | 1.87–1.95 | 40 epochs are enough (~13 instead of 40 min) |

- **Coverage first.** Same day, sweeps, scene and calibration, only the scan differs: 2.28 vs 13.57 mm. The network cannot place views it never saw, even with perfect labels (10.95). Coverage itself is the variable, not the kind of scan: in B the generic scan covered more (93 vs 75 %) and did better.
- **Then the map.** With ≥ 90 % coverage the error is about the map's camera error + 1 mm (C/D generic 5.2 → 5.1–6.4; E 4.3 → 5.9, 10.9 → 13.0). The exam-view scans gave the better maps (2.2–2.7 vs 5.2–10.9 mm).
- **Placement, not shape:** shape 1.3–3.9 mm for every current map, also where the absolute error is 13 mm (`runs/figures/volume_5XXA_run-501.png`: shifted, right shape).
- **No effect:** people moving in the background (D 2.24), scanning after instead of before the sweeps (2.50 vs 2.28).
- **Empty room:** the poorest maps of the session (4.3 and 10.9 mm camera): little structure for the depth alignment.
- **Outdated maps:** a large rearrangement is tolerated (B with A's map 4.28, as good as B's own scans); a very large one or an emptied room is not (13.9–59 mm), although the views were covered. Rescanning restores 3.11 (C).
- **The inlier gate (≥ 400) misses failures; the median inlier count does not:** current maps 1371–2213, the old map that works 1126, the ones that fail 23–450. A rescan warning without Polaris (threshold from this session only, not tuned). Low coverage and poor maps keep normal inlier counts (A generic 1456, E generic 1439): the coverage check is still needed.
- **Polaris reference** (`runs/polaris-check.md`, `runs/polaris-track.md`, `tools/check_polaris.py`): the marker was at the near edge of the Polaris volume (about 0.95 m) in every session, median 0.93 / 0.88 / 0.90 m in 3XX / 4XX / 5XX (80 / 86 / 97 % of samples nearer than 0.95 m). Tracker noise at the US image 0.24 / 0.25 / 0.12 mm, spikes 6 / 8 / 0 per min: 5XX has the cleanest reference. Our error shows no trend with distance (bands within ~1 mm, correlation −0.23 to +0.30, mixed signs). The reference is the same across sessions; a bias common to all sessions cannot be excluded without a second reference.
- **Seed fix:** room-504 starts with an arm in front of the camera, so the seed's depth ICP placed 3 frames and the map failed; `scr_map.py` now moves the seed 1 s later when it reaches < 1 s of the scan (`--seed-min-seconds`, `--seed-tries`); unchanged for every earlier map.

### 4.10 RGB-D SLAM baseline: ORB-SLAM3 (8 Nov)

ORB-SLAM3 RGB-D (`rgbd_tum`, default settings, 1250 ORB features, viewer off) on each session exported as one sequence, room scans first and then the sweeps (`tools/slam_baseline.py export`); scored like our system: one alignment and the camera calibration fitted on the room-scan frames only (3XX), the 3XX calibration reused for 4XX / 5XX (`--cam-calib-from runs/slam-3XX/slam_eval.json`, ORB-SLAM3's own, as ours reuses our 3XX one), 1 s smoothing (ours: 2 s in 3XX / 4XX, 1 s in 5XX). Same room scans as our maps (4XX D, E: C's scans; 5XX D: C's room-507). `runs/slam-*/slam_eval.md`, `runs/shape-slam.md`. Every frame tracked (100 %) on every run.

| split | ORB-SLAM3 map camera | ours map camera | **ORB-SLAM3** absolute / shape | **ours (no tracker)** absolute / shape | ours, Polaris labels | classical (Polaris map) |
|---|---|---|---|---|---|---|
| 3XX | 2.2 | 2.0 | **1.79 / 1.34** | 2.34 / 1.72 | 1.85 / 1.57 | 3.11 / 2.47 |
| 4XX A | 5.2 | 4.8 | **4.45 / 1.45** | 5.04 / 2.94 | 5.14 / 2.92 | 4.2 / 3.10 |
| 4XX B | 2.8 | 3.0 | **2.99 / 1.11** | 6.55 / 2.40 | 5.77 / 2.66 | 3.4 / 2.47 |
| 4XX C | 2.9 | 3.4 | **3.63 / 1.20** | 9.40 / 2.05 | 5.63 / 2.96 | 4.9 / 3.36 |
| 4XX D (C's scans) | 2.9 | C's | **3.63 / 1.28** | 11.54 / 3.10 | 9.63 / 3.16 | 6.3 / 3.61 |
| 4XX E (C's scans) | 2.6 | C's | **3.04 / 1.43** | 7.07 / 2.98 | 6.25 / 4.16 | 5.0 / 4.15 |
| **4XX mean** | | | **3.55 / 1.29** | 7.92 / 2.69 | 6.48 / 3.17 | 4.76 / 3.34 |
| 5XX A exam views | 4.0 | 2.7 | 3.29 / **1.15** | **2.28** / 1.90 | 1.85 / 1.67 | – |
| 5XX B exam views | 1.9 | 2.4 | **1.79 / 1.25** | 4.43 / 2.81 | – | – |
| 5XX C exam views | 1.7 | 2.2 | **1.88 / 1.17** | 3.11 / 1.76 | – | – |
| 5XX D (C's room-507) | 2.1 | 2.2 | 2.11 / **1.21** | 2.24 / 1.70 | – | – |
| 5XX E exam views (empty room) | 1.8 | 4.3 | **2.56 / 0.77** | 5.85 / 3.04 | – | – |
| **5XX mean (A–E)** | | | **2.33 / 1.11** | 3.58 / 2.24 | | |
| 5XX C, outdated (B's room-504) | 1.7 | – | **4.65 / 1.15** | 40.9 / 29.2 | | |
| 5XX E, outdated (C's room-507) | 1.6 | – | **3.06 / 0.85** | 13.9 / 14.6 | | |
| 5XX A generic (room-501) | no trajectory written (ORB-SLAM3 stopped; log needed) | | – | 13.57 / 3.79 | 10.95 / 3.93 | |

- **ORB-SLAM3, as run, is the most accurate tracker-free system:** absolute lower on 10 of 11 splits (on 5XX D within noise, 2.11 vs 2.24; ours lower only on 5XX A, 2.28 vs 3.29), shape better on all 11 (about half our shape error: 4XX 1.29 vs 2.69, 5XX 1.11 vs 2.24). It also beats the Polaris-mapped classical system (3XX 1.79 vs 3.11, 4XX 3.55 vs 4.76).
- **Not the map:** its room-scan maps are as good as ours (camera 1.7–5.2 vs 2.0–4.8 mm; better in the empty room E, 1.8 vs 4.3, worse in A, 4.0 vs 2.7). The difference is in the sweeps.
- **It does not need coverage:** where our coverage is low (4XX, 0–14 %) it is 2× better (3.55 vs 7.92); where coverage is ≥ 90 % and our map is good (5XX A, D) we are equal or better. Not because it maps the sweeps: with the map frozen after the room scan it is as good (like for like, below).
- **Scene changes, in the trajectory refined at shutdown:** with an outdated scan it relocalises on the static part and re-maps the rest (C with B's scan 4.65 vs our 40.9; E with C's 3.06 vs 13.9). Live it fails after the very large change too (below).
- **Shape:** frame-to-frame (k = 1, 8 rows) both are equal; over 1 s ours wanders twice as much (5XX A, k = 30: 0.86 / 0.56 vs 0.50 / 0.31 mm in / out of plane): per-frame localisation against a network does not keep a sweep rigid, temporal tracking with bundle adjustment does.
- **Like for like (9 Nov)**, below: the map from the room scan only and frozen, the poses as tracked. This was open here; it does not change the verdict.

**Like for like** (`tools/orbslam3/rgbd_online.cc`, README 6): mode `localize` maps the room scan, then localisation only (no new keyframes, no loop closing: the information our system has); `online.txt` = the pose of each frame as tracked (what a real-time system shows; mode `slam` = maps the sweeps too, as tracked). Upstream localisation mode never relocalises once lost (`Relocalization()` only in state LOST, which only the SLAM branch sets): every sweep after the first one or two was 0 % posed, so `Tracking.cc` is patched to relocalise on RECENTLY_LOST (one line, README 6; state it in the paper). Every split 98–100 % of frames posed after the patch except C with B's scan. Same evaluation (alignment + calibration on the room scan, 1 s smoothing); `runs/slam-*-loc/`, `runs/slam-*-online/`, `runs/shape-slam-fair.md`, per-sweep statistics `runs/stats-orbslam.md` (`tools/compare_stats.py`).

| split | ORB-SLAM3 localisation only, as tracked | ORB-SLAM3 SLAM, as tracked | ORB-SLAM3 SLAM, refined at shutdown | **ours** |
|---|---|---|---|---|
| 3XX | **1.84 / 1.30** | 1.81 / 1.18 | 1.79 / 1.34 | 2.34 / 1.72 |
| 4XX A | **4.47 / 1.43** | 4.51 / 1.31 | 4.45 / 1.45 | 5.04 / 2.94 |
| 4XX B | **3.80 / 1.10** | 3.31 / 4.26 | 2.99 / 1.11 | 6.55 / 2.40 |
| 4XX C | **4.90 / 1.25** | 5.47 / 3.13 | 3.63 / 1.20 | 9.40 / 2.05 |
| 4XX D (C's scans) | **4.64 / 1.58** | 4.69 / 1.16 | 3.63 / 1.28 | 11.54 / 3.10 |
| 4XX E (C's scans, occlusion) | 24.03 / 7.41 (run-426: 81.5) | 4.39 / 1.54 | 3.04 / 1.43 | **7.07** / 2.98 |
| **4XX mean (A–D)** | **4.45 / 1.34** | 4.50 / 2.47 | 3.68 / 1.26 | 8.13 / 2.62 |
| 5XX A exam views | 3.79 / 1.34 | 3.52 / 1.11 | 3.29 / 1.15 | **2.28** / 1.90 |
| 5XX B exam views | **1.70 / 1.17** | 1.79 / 1.22 | 1.79 / 1.25 | 4.43 / 2.81 |
| 5XX C exam views | **2.05 / 1.11** | 1.67 / 1.09 | 1.88 / 1.17 | 3.11 / 1.76 |
| 5XX D (C's room-507) | **1.60 / 1.74** | 1.53 / 1.17 | 2.11 / 1.21 | 2.24 / 1.70 |
| 5XX E exam views (empty room) | **2.65 / 0.99** | 2.23 / 0.79 | 2.56 / 0.77 | 5.85 / 3.04 |
| **5XX mean (A–E)** | **2.36 / 1.27** | 2.15 / 1.08 | 2.33 / 1.11 | 3.58 / 2.24 |
| 5XX A generic scan (0 % covered for us) | **2.88 / 1.19** | 3.16 / 1.09 | – | 13.57 / 3.79 |
| 5XX C, outdated (B's room-504) | 19.19 / 10.58, sweeps 5–8 only (1–4 not posed) | 43.69 / 3.51 (last sweep 3.3, after the map merge) | 4.65 / 1.15 | 40.9 / 29.2 |
| 5XX E, outdated (C's room-507) | **4.19 / 2.51** | 2.82 / 1.08 | 3.06 / 0.85 | 13.9 / 14.6 |

Bold: the better of localisation-only ORB-SLAM3 and ours (absolute). Paired by sweep (`runs/stats-orbslam.md`, ours smoothed 1 s): localisation only is lower on 49 of 63 sweeps of the current maps (Wilcoxon p < 0.001); 5XX A–E −1.05 mm [−1.68, −0.40]; ours lower on all 8 sweeps of 5XX A exam (+1.51 [0.93, 2.23]).

- **Localisation only is as good as full SLAM:** 4XX A–D 4.45 vs 4.50, 5XX 2.36 vs 2.15 mm. Mapping the sweeps is not where ORB-SLAM3's advantage comes from.
- **ORB-SLAM3 needs no coverage, also with the map frozen:** 5XX A generic scan 2.88 mm, ours 13.57 (10.95 with Polaris labels); 4XX (0–14 % covered) 4.45 vs 8.13. The coverage limit (limitation 1) belongs to SCR, not to mapping first and localising afterwards. ORB map points are 3D points with local descriptors and match from new viewpoints; the network has to regress coordinates for views it never saw. Caveat: in localisation mode ORB-SLAM3 still tracks frame to frame (motion model, visual odometry on temporary depth points when few map points match); the per-frame relocalisation run (mode `reloc`) separates the map from the tracking.
- **Where ours is better:** 5XX A exam-view scan (2.28 vs 3.79, every sweep), and 4XX E: on run-426 (an arm across the view 22–29 % of the time) localisation-only ORB-SLAM3 is 81.5 mm off for most of the sweep while reporting tracking OK (100 % posed); ours 6.9. The other occluded sweep (run-425) 4.03 vs 5.3; full SLAM handles both (3.15, 2.69). One case: a controlled occlusion test is open.
- **Outdated scan after a very large rearrangement:** both fail live (localisation only 19.2 mm on the 4 sweeps it posed, SLAM as tracked 43.7, ours 40.9); only the merged trajectory at shutdown recovers (4.65), which a live system never shows. A general limit of a map made before the exam. E with C's scan (emptied room): ORB-SLAM3 4.19, ours 13.9.
- **Run to run:** 4XX B and C SLAM as tracked lost the map or crashed in one run (B: room scan 29 % posed, sweeps 0 %; C: 2 of 4 sweeps) and ran cleanly in the next (3.31, 5.47 mm, but shape 4.26, 3.13). ORB-SLAM3 is multithreaded and not deterministic: repeats in 4.11.


### 4.11 ORB-SLAM3 per frame, repeats, occlusion; seeds and a leakage check (10–11 Nov)

Same protocol as 4.10 (alignment + calibration on the room scan, 1 s smoothing; ours smoothed 1 s in the paired statistics). `runs/stats-orbslam.md` (`tools/compare_stats.py`), `runs/slam-*-reloc/`, `-loc-r2/`, `-loc-r3/`, `runs/slam-5XX?-exam-occ*-*/`, `runs/track-v2map-5XX?-exam-occ*/`, `-seed*/`, `-gapfree/`.

**Per-frame relocalisation** (`rgbd_online … reloc`: the map from the room scan, frozen; before every sweep frame the tracking state is set to RECENTLY_LOST, so ORB-SLAM3 relocalises the frame against the map with nothing from the previous frame: the task of our network):

| split | ORB-SLAM3 per frame | ORB-SLAM3 localisation only (3 runs) | ours |
|---|---|---|---|
| 3XX | **1.72** | 1.84 / 1.63 / 1.74 | 2.36 |
| 4XX A / B / C / D / E | **4.14 / 3.70 / 4.93 / 4.44 / 5.03** | A 4.47 / 4.03 / 4.97; E 24.03 / 5.00 / 10.87 | 5.02 / 6.54 / 9.43 / 11.51 / 7.06 |
| **4XX mean (A–E)** | **4.45** | 8.37 / 4.33 / 5.64 | 7.91 |
| 5XX A / B / C / D / E (exam-view scans) | 3.90 / **1.63 / 2.27 / 1.63 / 2.23** | 5XX mean 2.36 / 2.31 / 2.27 | **2.28** / 4.43 / 3.11 / 2.24 / 5.85 |
| **5XX mean (A–E)** | **2.33** | | 3.58 |
| 5XX A generic scan (0 % covered for us) | **2.76** | 2.88 | 13.57 |
| 5XX C, outdated (B's room-504) | 19.97 on 3 of 8 sweeps (38 % of frames posed) | 19.19 on 4 of 8 | 40.85 |
| 5XX E, outdated (C's room-507) | **6.73** | 4.19 | 13.88 |

- **Its map is the advantage, not its tracking:** per frame, with nothing carried over from the previous frame, ORB-SLAM3 is as good as with tracking and better than ours on 52 of 63 sweeps (p < 0.001), and it still needs no coverage (generic scan 2.76 vs 13.57 mm). Its 3D map points with local descriptors match from viewpoints the room scan never had; the network does not extrapolate to them. Ours is better only on 5XX A exam (all 8 sweeps, 2.28 vs 3.90).
- **The forced relocalisation took effect:** it behaves differently from localisation only (outdated scan C: 7 % of sweep frames tracked; run-426 no longer fails: 4.32 mm). 25–41 ms per frame on the CPU (median; p90 65–80 ms), ours 60–70 ms on the GPU.
- **Run to run:** localisation only varies little except on the occluded sweep run-426: 81.5 / 4.65 / 28.2 mm over three runs, 4.32 per frame. The failure is real but random and comes from carrying a wrong pose from frame to frame.

**Controlled occlusion** (`occlusion.py`: a textured band at 0.4 m over 30 or 60 % of the image width, 3 s every 10 s, alternating sides, the same frames for both systems; room scans clear; 5XX B and C, 8 sweeps each). Mean of per-sweep medians, worst sweep in brackets (mm):

| block | occluded | **ours** | ORB-SLAM3 full SLAM, live | localisation only | per frame |
|---|---|---|---|---|---|
| B | none | 4.43 (6.3) | 1.79 | 1.70 | 1.63 |
| B | 30 % | 5.16 (7.5) | 1.76 | **17.91 (132.2)** | 1.78 |
| B | 60 % | 5.28 (8.5), 87 % of frames pass the gate | **6.88 (38.6)** | 3.32 (12.9) | **6.72 (39.7)** |
| C | none | 3.11 (5.1) | 1.67 | 2.05 | 2.27 |
| C | 30 % | 3.54 (6.1) | 2.12 | 2.48 | 2.01 |
| C | 60 % | 3.89 (6.6), 98 % pass | 2.67 (p90 6.2) | 2.65 (p90 8.3) | 2.22 on 3 of 8 sweeps (38 % of frames posed) |

- **Ours degrades gracefully:** +0.4–0.9 mm at 30 %, +0.8 mm at 60 %, no sweep above 8.5 mm; the gate drops the frames it cannot place (87–100 % pass).
- **ORB-SLAM3 is better on average but fails on single sweeps, in every mode:** 132 mm (B 30 %, localisation only), 38.6 (B 60 %, full SLAM), 39.7 (B 60 %, per frame), 12.9 (B 60 %, localisation only), each while reporting tracking OK (100 % of frames posed); per frame at 60 % on C it poses only 3 of 8 sweeps. Paired: at 60 % on B, ours is lower than full SLAM and per frame on average (+1.6 / +1.4 mm for ORB-SLAM3, intervals include 0); on C ORB-SLAM3 stays lower (−1.2 mm).
- **Shape under occlusion** (`runs/shape-reloc-occ.md`, after a rigid fit per sweep): at 60 % on B ours keeps 3.88 mm, ORB-SLAM3 7.35–8.44 in every mode (30 %: 3.38 vs 1.44–1.59, localisation only 6.14); on C ORB-SLAM3 stays better or equal (60 %: ours 2.80, ORB-SLAM3 1.83 / 2.29 / 3.20). Without the occluder: ours 2.81 (B), 1.76 (C); ORB-SLAM3 per frame 1.20, 1.06.
- Two blocks, one occluder; the failures are rare and random (three runs of the real occlusion block gave 81.5 / 4.65 / 28.2 mm on its occluded sweep). It supports "bounded error under occlusion" for ours, not "more accurate".

**Our seeds on 5XX** (map fixed, network trained with seeds 0 / 1 / 2): A 2.26 ± 0.03, B 4.20 ± 0.23, C 3.17 ± 0.12, D 2.22 ± 0.03, E 6.00 ± 0.27 mm (3XX 2.27 ± 0.08). The single-seed numbers of 4.9 stand.

**Leakage check:** smoothing each sweep as one piece (`track --smooth-across-gaps`) instead of restarting at the segment breaks, which Polaris dropouts decide: identical on all 11 splits to two decimals (most sweeps have one segment). Polaris does not reach the reported numbers through the smoothing.

## 5. Why SCR beats pose regression

| | RPR anchor network | SCR |
|---|---|---|
| output | one 6-DoF pose per image pair | ~3,600 room coordinates per image |
| pose computed by | the network | geometry (RANSAC + Kabsch on measured depth) |
| must learn | a general "image pair → motion" rule, valid across sessions | one room: "this patch is at (x, y, z)" |
| wrong content (hands, moved objects) | mixed into the pose | rejected as outliers |
| anchor error | 15 mm (3XX), 25–67 mm (4XX) | 1.8 mm (3XX), 5–9 mm (4XX) |

Precision comes from averaging thousands of 7–12 mm coordinate predictions in a rigid fit; geometry (intrinsics, depth, rigid transform) is left to an exact solver. Neither method generalises to unseen viewpoints; SCR is retrained per room, where memorising the room is the job.

## 6. US images (`tools/us_analysis.py`, `studies/li_baseline.py`; all negative)

| test | result |
|---|---|
| U1: in-plane registration (ECC) of frames 1–10 apart | worse than assuming no in-plane motion (e.g. 2XX k = 10: 1.91 vs 1.55 mm); the probe moves out of plane |
| U2: speckle decorrelation vs out-of-plane distance | same curve in every session and both subjects; distance from a 2XX curve 0.27–0.43 mm median error; magnitude only |
| U3: per-patch speckle (shift + 2 tilts) against the camera system | camera 2–5× better between nearby frames (3XX 0.07 / 0.19 / 0.24 vs 0.19 / 0.78 / 1.83 mm at 1 / 4 / 8 rows); no fusion helps |
| Li et al. (TBME 2024) reproduced on its own data | 21.4 ± 11.2 mm accumulated error vs 22.8 ± 17.5 published (zero motion 73.1) |
| Li et al. on our sweeps (accumulated error, 3XX / A / D) | zero-shot 129 (3XX); fine-tuned 75 / 125 / 82; from scratch 56 / 49 / 52 = zero motion 58 / 49 / 53; camera 15–30× better at 1 s |

The remaining error is long-range (sweep-scale), which speckle cannot see; a learned sensorless network learns its training protocol, not our motion.

## 7. Limitations

1. **Coverage:** SCR does not extrapolate to viewpoints the room scan missed, even with perfect labels (5XX A generic scan: 10.95 mm with Polaris labels, 4.9); classical anchors cope better with short scans (4XX: 1.4× with each block's scans, 1.15× with all scans of the day; 4.3). The room scan has to follow the exam views.
2. **The camera calibration needs a reference once per probe** (Polaris here, a phantom in deployment), and the 3XX calibration placed the 4XX sweeps less well (Table G). The benchmark tables A–E use Polaris-built maps (the oracle map); the tracker-free system is Tables F, G.
3. **3XX room scans partly recorded after the sweeps:** with the map recorded before the sweeps SCR is on par with classical, not better (4.7); report both numbers.
4. **Small test sets, one room, two subjects and one phantom** (5 + 26 + 32 sweeps); seed spread measured on 3XX only (1.85–2.12 mm). A bare room gives a poor map (5XX E).
5. **Real time:** tested offline on recorded data (3.3); not yet run live on the hardware.
6. The inlier gate was chosen after seeing the test splits (no effect on system results).
7. Hand–eye calibration (3.5 mm board-corner error) enters labels and ground truth.
8. The probe marker was at the near edge of the Polaris volume (median 0.88–0.93 m) in every session; the error shows no trend with distance, but a bias common to all sessions cannot be excluded (4.9). Future recordings: Polaris 1.0–2.0 m from the probe (`tools/check_session.py` warns).
9. **ORB-SLAM3 RGB-D is more accurate than our system, also like for like** (map from the room scan only, then frozen; poses as tracked): 49 of 63 sweeps, and it needs no coverage (4.10). Its localisation mode needed a one-line patch to relocalise after losing track. Per-frame relocalisation keeps it ahead, so its map is better than ours, not just its tracking (4.11). No accuracy claim against RGB-D SLAM; what our system offers is bounded error under occlusion (two blocks, one synthetic occluder) and RGB-only coordinates (not tested).

## 8. Open tasks

Done (7 Nov): session 5XX recorded and run (4.9: coverage, map quality, scene changes, outdated maps, oracle on A, combined scans, training length, Polaris check, volume figure of A). Done (4 Nov): the reproduction from scratch with the cleaned code, three seeds, loop closures and camera calibration as clean ablations (Table F), 4XX with the 3XX calibration, pooled scans, strict protocol, real time on 4XX, 3D pages (Table G). Still open (`note.md` 1 has the commands):

| # | task | type | needs |
|---|---|---|---|
| 1 | 4XX C / D placement: refit the camera calibration on the 4XX scans (diagnostic, uses that session's Polaris), retrain, track | analysis | **done 5 Nov:** C 9.40 → 7.87, D 11.54 → 9.58 (= oracle 9.63), shape unchanged: the calibration transfer explains 1.5–2.0 mm, the rest of C is the map |
| 2 | RGB-D SLAM baseline (ORB-SLAM3 RGB-D) on room scan + sweeps, scored after the same one alignment per session | comparison | **done 8–9 Nov (4.10):** better than ours, also like for like (localisation only after the room scan: 49 of 63 sweeps; no coverage needed) |
| 3 | classical anchors on our own tracker-free map (same map, network vs SIFT) | comparison | **done 5 Nov:** 3XX SCR 2.35 / 1.73 vs SIFT 3.65 / 2.66; 4XX SIFT 5.78 vs SCR 7.92 (gap to classical: ~2.1 mm method, ~1.0 mm map); 4XX shape to run |
| 4 | why the 2XX map fails (each scan alone, stricter joining, own calibration) | analysis | **done 5 Nov:** room-201 carries the bad stretch (1 s motion p90 31 mm alone); room-202 alone is clean; strict joining worse (9.52 vs 8.13) |
| 5 | static 3D volume figures for the paper (true vs tracker-free, also after the rigid fit) | figure | **done 5 Nov** (`runs/figures/`); re-run after the title fix |
| 6 | end-to-end fine-tuning through a differentiable Kabsch (DSAC*-style) | ablation, optional | code |
| 7 | a session with ~1 min room scans along the exam viewpoints; live run on the hardware | data, deployment | **5XX recorded and run (4.9)**; live run still open |
| 8 | go / no-go before the exam without Polaris: coverage from the self-made map poses, median-inlier warning for an outdated map; tested on every 4XX / 5XX track | method | code |
| 9 | update an outdated map by fine-tuning on a short new scan instead of rescanning from scratch (C: B's network + room-507) | method | `train --init` (code) |
| 10 | classical pipeline on 5XX (Polaris map and our map) | comparison | SIFT odometry caches + anchor pairs in rgbd-us |
| 11 | error against coverage, all sweeps of 3XX–5XX in one plot | figure | `tools/coverage_error.py` on track outputs (code) |
| 12 | ORB-SLAM3 per-frame relocalisation against the frozen room-scan map (no frame-to-frame tracking): is its map or its tracking the advantage? | comparison | **done 10 Nov (4.11):** the map: per frame it stays ahead (52 of 63 sweeps), no coverage needed |
| 13 | ORB-SLAM3 repeats (3 runs of localisation only) | comparison | **done 10 Nov (4.11):** stable except the occluded sweep run-426 (81.5 / 4.65 / 28.2 mm) |
| 14 | controlled occlusion, both systems on the same frames (`occlusion.py`; 5XX B, C; 30 and 60 % of the width) | robustness | **done 11 Nov (4.11):** ours degrades gracefully (worst sweep 8.5 mm), ORB-SLAM3 lower on average but fails on single sweeps by 13–132 mm |
| 15 | smoothing without the Polaris segment breaks (`track --smooth-across-gaps`): ground truth must not decide where smoothing restarts | check | **done 10 Nov (4.11):** identical to two decimals |
| 16 | three seeds on 5XX (seed spread so far on 3XX only) | statistics | **done 10 Nov (4.11):** sd 0.03–0.27 mm |
| 17 | framing of the paper after 12 and 14: per-frame localiser / robustness, RGB-only, or a study of what decides tracker-free probe tracking | paper | decision |

### 8.1 History of the map without a tracker (2 Nov, earlier code)

**Map without a tracker, first result (3XX, 2 Nov; `runs/map-3XX`, `runs/v2map-3XX`, `runs/track-v2map-3XX`).** The map covers all 3,356 room-scan frames (88 % after round 1, 100 % after round 2). Against Polaris, after one rigid alignment on the points 1 m in front of each camera: scene points 9.0 / 16.0 mm (median / p90), camera position 15.3 mm, rotation 0.93°, relative motion over 1 s 7.2 / 18.5 mm. The first alignment used the camera positions only; that left a 17° rotation and 50.6 mm tracking. Tracking with the network trained on these labels: **12.78 mm** at the US image (2 s smoothing; per sweep 8.2–18.2; 100 % of frames posed; step over 8 rows 1.39 mm), against 1.85 mm with Polaris labels and 3.1 mm for the classical system. The network follows its labels: its camera error (15 mm) is the map's. Compared with the Polaris-labelled track (a proxy for Polaris, points near the camera), most of the difference remains after a rigid fit of each sweep (3.4–10.9 mm), and the frame-to-frame jitter is the same (0.6–1.1 mm). So the error is a smooth bend of the map, not noise and not only a rigid offset. Its likely source is the 7 mm error of the map's 1 s relative motion: each frame is localised on its own, so nothing ties neighbouring frames together. **Shape confirms it** (`runs/shape-map-3XX.md`, US image, mm): absolute 13.26, shape **8.54** (per sweep 4.8–14.0), against 1.85 / 1.57 with Polaris labels, 3.11 / 2.47 for classical and 9.43 / 6.23 for odometry only. The error grows with the time between frames: 1 frame 0.12 / 0.08 (in / out of plane; Polaris labels 0.08 / 0.08), 8 rows 0.76 / 0.46 (0.50 / 0.37), 1 s 2.21 / 1.14 (1.07 / 0.62), whole sweep 8.5 (1.6). Frame to frame it is as good as with Polaris labels; over seconds the map bends. Conclusions: (1) a map without a tracker works end to end (every frame mapped and tracked, no failure); (2) the network's accuracy is set by its labels (1.85 → 13 mm with the same network), so in a new room the map's quality decides the result; (3) a map localised frame by frame is not good enough: its shape is worse than odometry alone. It needs constraints between neighbouring frames (ICP pose graph); target before training: 1 s relative motion ≤ 1 mm, scene points ≤ 3 mm.

**Pose graph (3XX, 2 Nov; `runs/map-3XX-graph`, `runs/v2graph-3XX`, `runs/track-v2graph-3XX`, `runs/shape-graph-3XX.md`).** `scr_map.py --from runs/map-3XX` adds depth-ICP edges between room-scan frames 1, 5, 15 and 30 rows apart (started from the map's relative pose) to each frame's network pose (prior on its view points, 10 mm), robust least squares. Map against Polaris: scene points 9.0 → **6.9** / 12.0 mm, camera position 15.3 → 11.6 mm, rotation 0.93 → 0.76°, 1 s motion 7.2 → **3.4** / 8.4 mm (target 1 mm not reached). A 30 mm prior gives 7.3 mm and the same 3.4 mm 1 s motion. Tracking with the network trained on the graph labels: 12.49 mm at the US image (2 s smoothing; per sweep 11.4–15.6; p90 14.6, was 22.2; step over 8 rows 1.14 mm, was 1.39). Shape **4.74 mm** (was 8.54; per sweep 1.9, 3.4, 4.4, 4.2, 9.8), better than odometry alone (6.23), worse than Polaris labels (1.57) and classical (2.47). Out-of-plane over 1 s 1.24 mm (Polaris labels 0.62). The absolute error now sits in one offset: compared with the Polaris-labelled track, the difference is a fixed transform in the camera frame (9.6 mm, mostly along camera x, and 0.4°), the same in all five sweeps to 1–2 mm, while in room coordinates it varies by up to 5 mm. A fixed camera-frame transform is what a hand–eye mismatch looks like: Polaris labels and Polaris ground truth share the hand–eye calibration (limitation 7), so its error cancels for the Polaris-labelled network but not for a map built from the camera alone. Removing one such transform, estimated on the other four sweeps, brings the difference to the Polaris-labelled track from 8.4–12.2 to 2.2–4.3 mm (run-317 7.9). Proxy only; the proper test estimates the transform from the room scan (map vs Polaris) and evaluates the sweeps with it.

Files and commands: `README.md`.
