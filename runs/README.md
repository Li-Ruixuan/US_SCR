# runs/: index of all results

Every folder backs a number in `../summary.md` (section in the last column). Checkpoints (`best.pt`) are on the training PC only. Errors are camera position error against Polaris, **mean of per-sweep medians / pooled p90 (mm)**, rotation median, one frame per second, unless noted.

Status: **final** = the reported model / result; **study** = part of an ablation or analysis in the paper or summary; **negative** = tried, not adopted; **check** = sanity check.

## How to read the files

| file | content |
|---|---|
| `<run>/config.json` | all training settings, number of frames and steps, code version (`git`), errors of estimated labels if any |
| `<run>/history.json` | per epoch: loss, train-mode error, learning rate, time; every few epochs the fit check (`fit`: coordinate error on training frames, the same after a rigid fit, PnP pose of those frames) |
| `<run>/eval_<test>[_<sweeps>][_kabsch]/scr_eval.md` | anchor accuracy per sweep (position and rotation median / p90, solved share, inliers, ms per frame); without `_kabsch`: PnP solve; with: Kabsch solve on the measured depth |
| `.../scr_eval.json` | the same per frame |
| `sys-*/anchor_eval_*.md` | full system (rgbd-us `anchoring.py`): per sweep the anchors (count, accepted, error, rotation), then the **median error at the US image** with the mean step-to-step error in brackets for: no anchors, causal, offline, **offline pose graph** (the reported column) |
| `volume3d-*/<run>.html` | interactive 3D compounding (open in a browser); mean pixel error of each pose source on the page |

## 1. Final models (small head, 120 epochs, room scans only)

| run | map → test | PnP | **Kabsch** | status |
|---|---|---|---|---|
| `s1-e120-2XX` | 2XX → run-205, 211 (validation) | 5.1 / 11.3 | **3.4 / 8.7**, 0.33° | final (validation) |
| ″ `eval_train_3XX*` | 2XX → 3XX (outdated map) | 21.2 / 47.8 | 6.5 / 11.8 | final |
| `v1-3XX` | 3XX → 3XX | 2.5 / 5.4 | **2.0 / 3.3**, 0.19° | final |
| `v1-3XX-seed1`, `v1-3XX-seed2` | same, seeds 1, 2 | | 1.9 / 3.6, 2.2 / 3.8 | final (seed spread) |
| `v1-4XXA` | A → A | 9.9 / 17.6 | **5.9 / 10.1**, 0.48° | final |
| ″ `eval_test_4XXB*`, `eval_test_4XXC*` | A → B, A → C (outdated maps) | 31.7 / 47.3, 47.4 / 65.2 | 14.0 / 25.4, 13.4 / 113 | final |
| `v1-4XXA-seed1` | A → A, seed 1 | | 5.8 / 10.1 | final (seed spread) |
| `v1-4XXB` | B → B | 8.6 / 17.8 | **5.9 / 9.2**, 0.40° | final |
| `v1-4XXC` | C → C, and C's map → D, E | C 11.2, D 15.4, E 10.2 | **C 5.2 / 10.1, D 9.3 / 18.9, E 5.9 / 13.9** | final |

## 2. Training study (2XX validation; summary 3.1, 3.13)

| run | change | PnP | Kabsch | status |
|---|---|---|---|---|
| `s1-base-2XX` | first SCR recipe (Huber 50 mm, one-cycle, 15 epochs, every 2nd frame, fp16 head) | 15.8 / 31.3 | | study |
| `s1-e120-seed1-2XX` | 120 epochs, seed 1 | 4.8 / 9.4 | 3.5 / 9.4, 0.37° | study (seed spread) |
| `big-2XX` | big head (2.18 M) | 4.6 / 9.6 | 3.4 / 8.0, 0.29° | study |
| `clean-2XX` | labels < 2 m, no depth edges | 6.1 / 10.3 | 3.5 / 8.0, 0.31° | study |
| `bigclean-2XX`, `bigclean-seed1-2XX` | big head + clean labels, seeds 0 and 1 | 5.0 / 10.9 | 3.4 / 7.3, 0.27°; 3.7 / 6.9, 0.28° | adopted (lower p90 and rotation for both seeds); not yet run on the test splits |

The Kabsch refinement variants (`--kabsch-refine weighted/joint`, removed from the code) and the room-202-only validation split were deleted on 24 Oct; their numbers are in summary 3.5 and 3.10, the files in git (commit 5f80808).

## 3. Map extension (4XX; summary 3.10–3.12)

Test only on later sweeps: A on run-405…408, D on run-421, 423, 424 (Kabsch).

| run | map | Kabsch | status |
|---|---|---|---|
| (`v1-4XXA` on the same sweeps) | room scans only | 5.3, 0.47° | reference |
| `v1-4XXA-plus2` | + run-401, 402 | 1.9 / 5.4, 0.23° | study |
| `v1-4XXA-plus4` | + run-401…404 | 1.9 / 5.5, 0.22° | study |
| `bigclean-4XXA-plus4` | + run-401…404, big head + clean labels | 1.8 / 5.2, 0.22° | study |
| `selflabel-4XXA` | full system with the room-scan model on run-401, 402, started from an SCR anchor (no Polaris): the estimated labels | anchors 5.5 / 7.7; US image 5.2 | input |
| `v1-4XXA-plus2-est` | + run-401, 402 labelled with those estimates | 5.0 / 8.4, 0.48° | negative |
| (`v1-4XXC` on the same sweeps) | C's room scans only | 9.0, 0.76° | reference |
| `v1-4XXD-plus3` | + run-418…420 (Polaris labels) | 3.1 / 7.0, 0.22° | study |
| `selflabel-4XXD` | full system on run-418…420, no Polaris | anchors 9.4 / 17.5; US image 10.3 | input |
| `v1-4XXD-plus3-est` | + run-418…420 labelled with those estimates | 7.9 / 11.2, 0.60° | negative |

## 4. Full system: error at the US image (median, offline pose graph; summary 3.7, 3.10, 3.11, 3.13)

| run | anchors | US image (step-to-step) | status |
|---|---|---|---|
| `sys-kabsch-4XXA-plus4`, `sys-kabsch-4XXD-plus3` | SCR on extended maps | A 2.3, D 4.5 | study |
| `sys-classical-4XXA-plus4`, `sys-classical-4XXD-plus3` | classical anchors with the same extra keyframes | A 3.2, D 5.8 | study (fair comparison) |
| `sys-scronly-2XX`, `-3XX`, `-4XXA` | SCR anchors every 0.25 s, no odometry (read the "offline" column) | 2XX 3.8 (2.87), 3XX 2.1 (1.69), A 5.9 (1.85) | study |

The v1 system runs with segments started at the true pose (`sys-kabsch-2XX`, `-3XX`, `-4XXA` … `4XXE`, `sys-kabsch-nogate-4XXD/E`; summary 3.7, 3.13) and their 3D pages (`volume3d-3XX`, `volume3d-4XX`) were removed on 27 Oct: superseded by `sys-final-*` (same model, started from an anchor, same results) and section 7. Numbers in the summary, files in git commit 1648fcf.

Classical + classical references are in rgbd-us (`runs/anchoring-classical-*`, `runs/val-classical-2XX`): 2XX 4.2, 3XX 3.2, A 4.2, B 3.4, C 4.6, D 6.3, E 4.8 mm.

## 5. Other analyses

| run | content | status |
|---|---|---|
| `coverage_error.md` | anchor error vs distance to the nearest room-scan pose (PnP, v1 models): covered 4.1, uncovered 13.4 mm | final |
| `us-2XX`, `us-3XX`, `us-4XXA`, `us-4XXD` | US diagnostics: in-plane registration (U1, no better than zero motion) and speckle decorrelation vs out-of-plane distance (U2, transfers across sessions) | study |

## 6. Added 24 Oct (summary 3.14)

| run | content | key result | status |
|---|---|---|---|
| `v1-3XX-room301` | 3XX mapped on room-301 only (recorded before run-315…317), tested on run-315…317 | Kabsch 3.1 / 6.1, 0.26° (both scans: 1.8) | final (strict-protocol check) |
| `sys-classical-3XX-room301` | classical anchors, same map and sweeps, start from anchors | anchors 2.7 / 6.1, 0.32°; US image 3.0 | final (strict-protocol check) |
| `sys-final-3XX` | full system, v1 model, every segment started from an anchor (`--start anchor`) | US image 2.6 | study (seed spread with the next row; superseded by `sys-v2r-3XX`) |
| `sys-final-3XX-seed1`, `-seed2` | same, models of seeds 1 and 2 | 2.7, 2.7 | final (seed spread) |
| `sys-classical-final-2XX` | classical anchors, 2XX validation, start from anchors (the 3XX and 4XX ones are in rgbd-us `runs/anchoring-classical-*`, files with `startanchor`) | 4.2 | final (reference) |
| `v2-3XX`, `v2-4XXA`, `v2-4XXB`, `v2-4XXC` | big head + clean labels on the test splits (`v2-4XXC` also on D, E) | Kabsch 3XX 1.8, A 5.4, B 5.6, C 4.8, D 8.6, E 5.7 | study (small gain on every split) |

## 7. Final configuration (24–27 Oct; summary 3.15, 3.16, 3.8)

| run | content | key result | status |
|---|---|---|---|
| `sys-v2r-2XX` | v2 (`bigclean-2XX`) + gate recovery 3; also `--scr-frames 3`, `5` | US image M = 1 4.2, M = 3 4.4, M = 5 4.5 mm | final (validation); multi-frame negative |
| `sys-v2r-3XX`, `sys-v2r-4XXA` … `4XXE` | **final SCR system**: v2, gate recovery 3, start from anchors, pose graph | US image 3XX 2.6, A 5.0, B 5.7, C 5.9, D 9.6, E 6.5 | final |
| `sys-classical-r-3XX`, `-4XXA` … `4XXE` | **final classical system**, same settings | 3XX 3.1, A 4.2, B 3.4, C 4.9, D 6.3, E 5.0 | final |
| `volume3d-final/<split>/run-*.html` | 3D pages of the two final systems + odometry only, every sweep (31) | mean pixel error 3XX 2.7 vs 3.2, A 5.3 vs 4.4, B 6.0 vs 3.7, C 6.9 vs 5.3, D 10.5 vs 7.2, E 7.8 vs 5.2 mm | final (figure) |
| `us-speckle-3XX`, `-4XXA`, `-4XXD` | U3: per-patch speckle (curve from 2XX) against the final SCR system | system 2–5× better than speckle at 1–8 rows; no fusion helps | negative |
| `us-speckle-2XX` | U3 on 2XX validation (curve `curve.json`, leave one sweep out) | system 0.10 / 0.44 / 0.77 vs US 0.27 / 0.72 / 1.45 mm | negative |
| `shape-final.md`, `.json` | shape of the reconstruction: error after a rigid fit of each sweep, relative error between frames (summary 3.17) | 4XX shape SCR 3.5 vs classical 3.3 mm (absolute 1.2–1.7× worse) | final |
| `volume3d-final/2XX/` | 3D pages of 2XX validation (run-205, 211) | | final (figure) |

## Removed runs (27 Oct)

Removed to keep this folder to what the paper and summary need; the files are in git commit 52d7892 (`git show 52d7892:runs/<run>/<file>`), the checkpoints on the training PC. Key numbers (2XX validation, PnP mean of medians / p90 unless noted):

| run | content | key result |
|---|---|---|
| `s0a-scr-3XX` | first SCR's checkpoint re-evaluated (evaluator check) | 9.8 / 22.1 on 3XX, reproduces rgbd-us |
| `s1-2XX` | S1 recipe, 30 epochs | 6.3 / 13.1 |
| `s1-e60-2XX`, `s1-e60-seed1-2XX` | 60 epochs, seeds 0 and 1 | 5.4 / 11.3, 6.3 / 12.9 |
| `s3-full-2XX` | 720 × 1280 input, 30 epochs | 7.3 / 14.5 (negative) |
| `aug-2XX`, `aug-4XXA` | viewpoint augmentation | 2XX Kabsch 6.5 / 10.1; A Kabsch 5.1 / 8.1 (negative) |
| `v1-4XXA-plus1` | map + run-401 | Kabsch 2.4 / 6.6, 0.27° |
| `sys-final-2XX`, `-4XXA` … `4XXE` | v1 full system, start from anchors | US image 4.3; A 5.5, B 6.0, C 6.7, D 10.3, E 6.6 |
| `sys-v2-4XXA`, `-4XXB`, `-4XXC` | v2 full system without gate recovery | run-404 locked out (US image 28.3 → 8.2 mm with recovery) |

## 8. Li et al. reproduction (27 Oct; summary 3.18)

| run | content | key result | status |
|---|---|---|---|
| `li-repro-M2` | Li et al. (TBME 2024) baseline M = 2, their code and forearm data, 20,000 epochs; `saved_model/` (weights, not in git from now on) | accumulated error 21.4 ± 11.2 mm vs paper 22.8 ± 17.5; zero motion 73.1 | final (reproduction) |
| `li-transfer/zeroshot-2XX-asis`, `-swap` | their weights on 2XX validation, two axis mappings | as-is 199 vs swap 218 mm (zero motion 32): as-is chosen | input |
| `li-transfer/zeroshot-3XX` | their weights on 3XX | 129.0 mm (zero motion 57.8) | negative |
| `li-transfer/ft-2XX`, `scratch-2XX` | fine-tuned from their weights / from scratch on our 2XX (weights in `saved_model/`, not in git) | validation corner distance 0.57 / 0.54 mm | input |
| `li-transfer/ft-3XX`, `-4XXA`, `-4XXD` | fine-tuned, tested | 75.2, 125.4, 81.7 mm (zero motion 57.8, 49.3, 53.3) | negative |
| `li-transfer/scratch-3XX`, `-4XXA`, `-4XXD` | from scratch, tested | 56.0, 49.1, 52.4 mm: = zero motion | negative |

The smoke test (`li-repro-smoke`, 20 epochs) was removed.
