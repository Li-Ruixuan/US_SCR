# runs/: index of the results

Every folder backs a number in `../summary.md` (section in the last column). Checkpoints (`best.pt`, `saved_model/`) are on the training PC only. Unless noted: anchors = camera position error against Polaris, mean of per-sweep medians / pooled p90 (mm), rotation median, one frame per second; system = median error at the US image (mm), step-to-step error over 8 rows in brackets.

## How to read the files

| file | content |
|---|---|
| `<model>/config.json`, `history.json` | training settings and code version; per epoch loss, learning rate, time and the fit check on training frames |
| `<model>/eval_<test>[_<sweeps>][_kabsch]/scr_eval.md`, `.json` | anchor accuracy per sweep (`scr_anchor.py eval`; `_kabsch` = Kabsch solve, else PnP) |
| `track-*/scr_track.md`, `.json`, `poses.npz` | single-network system (`scr_anchor.py track`): raw and smoothed, per sweep; the raw poses per row |
| `sys-*/anchor_eval_*.md`, `.json` | hybrid system (`anchoring.py` via `tools/anchoring_kabsch.py`): per sweep anchors, then the US-image error for no anchors, causal, offline, **offline pose graph** (the reported column) |
| `volume3d/index.html`, `volume3d/<split>/<run>.html` | 3D pages (open in a browser): true poses vs the single network, the classical system and odometry only; the index lists every sweep with its mean pixel error |
| `us-*`, `us-speckle-*`, `shape-final.*` | `tools/us_analysis.py inplane / speckle / shape` |
| `li-repro-M2`, `li-transfer/*` | `tools/li_baseline.py repro / transfer` |

## 1. Final system: one network on every frame (summary 3.1)

| run | model | 2 s smoothed (raw) |
|---|---|---|
| `track-2XX` | `bigclean-2XX`, validation run-205, 211: chooses the window | 3.35 (1.20) [raw 3.59] |
| `track-3XX` | `v2-3XX` | **1.85 (0.93)** [2.03] |
| `track-4XXA` | `v2-4XXA` | 5.14 (0.99) [5.21] |
| `track-4XXD` | `v2-4XXC` | 9.63 (1.34) [9.57] |
| `track-4XXB`, `track-4XXC` | `v2-4XXB`, `v2-4XXC` | 5.77 (0.92), 5.63 (0.82) |
| `track-4XXE` | `v2-4XXC` | 6.25 (1.68) [raw 6.12] |
| `track-3XX-seed1`, `-seed2` | `v2-3XX-seed1`, `-seed2` | 1.95 (0.92), 2.12 (0.93) |
| `track-3XX-room301` | `v2-3XX-room301` (map room-301 only), run-315…317: strict protocol | 2.98 (1.18) [3.12]; classical system 3.0 |
| `track-v2pool-4XXB` | `v2pool-4XXB` (room-401…404): final for B | 3.76 (0.83) |
| `track-v2pool-4XXC`, `-4XXD`, `-4XXE` | `v2pool-4XXC` (all same-day room scans, room-401…406): final for C, D, E | 3.98 (0.79), 8.46 (1.17), 5.92 (1.56) |

3D pages of these runs: `volume3d/` (index: `volume3d/index.html`; `*-pool` = pooled same-day scans, both systems).

## 2. Final models (v2: big head + clean labels, 120 epochs, room scans only; summary 4.2)

| run | map → test | anchors (Kabsch) |
|---|---|---|
| `bigclean-2XX`, `bigclean-seed1-2XX` | 2XX → run-205, 211 (validation; seeds 0, 1) | 3.4 / 7.3, 0.27°; 3.7 / 6.9, 0.28° |
| `v2-3XX` | 3XX → 3XX | 1.8 / 3.4, 0.19° |
| `v2-3XX-seed1`, `-seed2`; `v2-3XX-room301` | 3XX, seeds 1, 2; map room-301 only | (tracked only, section 1) |
| `v2-4XXA`, `v2-4XXB` | A → A, B → B | 5.4 / 8.9, 0.45°; 5.6 / 8.0, 0.35° |
| `v2-4XXC` | C → C, D, E | 4.8 / 9.9; 8.6 / 14.5; 5.7 / 9.7 |
| `v2pool-4XXB` | room-401…404 (A + B scans, 6,274 frames) → B | (tracked only, section 1) |
| `v2pool-4XXC` | room-401…406 (A + B + C scans, 8,671 frames) → C, D, E | (tracked only, section 1) |

## 3. Hybrid system: anchors + SIFT odometry + pose graph (summary 3.1, 3.2, 4.8)

| run | content | US image |
|---|---|---|
| `sys-v2r-3XX`, `-4XXA` … `-4XXE` | SCR v2 anchors every 1 s, gate recovery, start from an anchor | 3XX 2.6, A 5.0, B 5.7, C 5.9, D 9.6, E 6.5 |
| `sys-v2r-2XX` | same on 2XX; also `--scr-frames 3, 5` (multi-frame anchors, negative) | 4.2; 4.4, 4.5 |
| `sys-classical-r-3XX`, `-4XXA` … `-4XXE` | classical anchors, same settings | 3XX 3.1, A 4.2, B 3.4, C 4.9, D 6.3, E 5.0 |
| `sys-classical-final-2XX` | classical anchors on 2XX | 4.2 |
| `sys-classical-pool-4XXB` … `-4XXE` | classical anchors with the pooled same-day map (as `v2pool-*`) | B 5.5, C 21.1, D 18.9, E 10.2 (worse) |
| `shape-final.md`, `.json` | shape after a rigid fit of each sweep: single network (`scr-track`), classical system, odometry only | 2XX 3.04 vs 3.98; 3XX 1.57 vs 2.47; 4XX 3.17 vs 3.34 (pooled scans: 2.95) |

## 4. Studies

| run | content | key result | summary |
|---|---|---|---|
| `s1-base-2XX`, `s1-e120-2XX`, `s1-e120-seed1-2XX` | first SCR recipe; fixed recipe 120 epochs (v1; seed 1); `s1-e120-2XX` also on 3XX (outdated map) | PnP 15.8 → 5.1 (4.8); Kabsch 3.4 (3.5); 2XX → 3XX 6.5 | 4.1, 4.4 |
| `big-2XX`, `clean-2XX` | big head; clean labels (alone) | Kabsch 3.4 / 8.0, 0.29°; 3.5 / 8.0, 0.31° | 4.5 |
| `v1-3XX`, `v1-3XX-seed1`, `-seed2`, `v1-4XXA`, `v1-4XXA-seed1`, `v1-4XXB`, `v1-4XXC` | v1 (small head) on the tests; `v1-4XXA` also A → B, A → C | 3XX 2.0 / 1.9 / 2.2; A 5.9 / 5.8; B 5.9; C 5.2, D 9.3, E 5.9; A → B 14.0, A → C 13.4 | 4.2, 4.4 |
| `sys-final-3XX`, `-seed1`, `-seed2` | v1 hybrid system, 3 seeds | 2.6, 2.7, 2.7 | 4.2 |
| `coverage_error.md` | anchor error vs distance to the nearest room-scan pose | covered 4.1, uncovered 13.4 | 4.3 |
| `v1-4XXA-plus2`, `-plus4`, `bigclean-4XXA-plus4`, `v1-4XXD-plus3` | map + earlier sweeps (Polaris labels) | A 1.9, 1.9, 1.8; D 3.1 | 4.3 |
| `sys-kabsch-4XXA-plus4`, `-4XXD-plus3`; `sys-classical-4XXA-plus4`, `-4XXD-plus3` | systems on the extended maps | SCR A 2.3, D 4.5; classical 3.2, 5.8 | 4.3 |
| `selflabel-4XXA`, `-4XXD` → `v1-4XXA-plus2-est`, `v1-4XXD-plus3-est` | extra sweeps labelled with the system's own poses | A 5.0, D 7.9 (negative) | 4.3 |
| `v1-3XX-room301`, `sys-classical-3XX-room301` | strict protocol: map room-301 only, test run-315…317 | SCR 3.1 / 6.1, 0.26°; classical 2.7 / 6.1, system 3.0 | 4.7 |
| `sys-learned-2XX`, `-3XX`, `-4XXA`, `-4XXD` | without SIFT: RPRNet odometry (`odometry-recover3` = 1 s, `odometry-every0.25s`), or none (`odometry-odo-zero-every0.25s`) | 0.25 s + RPRNet 3.2 / 5.4 / 9.9; SCR alone raw 2.0 / 5.2 / 9.7 | 4.6 |
| `v2fz-4XXA`, `v2rv-4XXA`, `v2fzrv-4XXA` → `track-v2fz-4XXA`, `track-v2rv-4XXA`, `track-v2fzrv-4XXA` | training strategies on 4XX A: frozen encoder, rendered views (`render_preview.jpg`), both | 5.24, 4.98, 5.51 vs 5.14 (none adopted) | 4.5 |
| `v2e240-4XXA` → `track-v2e240-4XXA` | 240 instead of 120 epochs on 4XX A | 5.28 vs 5.14 (not adopted) | 4.5 |

## 5. US images (all negative; summary 6)

| run | content | key result |
|---|---|---|
| `us-2XX`, `us-3XX`, `us-4XXA`, `us-4XXD` | U1 in-plane registration; U2 speckle decorrelation | U1 no better than zero motion; U2 distance 0.27–0.43 mm |
| `us-speckle-2XX` (curve), `-3XX`, `-4XXA`, `-4XXD` | U3 per-patch speckle against the SCR system | camera 2–5× better; no fusion helps |
| `li-repro-M2` | Li et al. reproduced on their data | 21.4 ± 11.2 vs 22.8 ± 17.5 mm published |
| `li-transfer/zeroshot-*`, `ft-*`, `scratch-*` | Li et al. on our sweeps (zero-shot; axis mapping as-is chosen on 2XX) | zero-shot 129, fine-tuned 75–125, scratch 49–56 = zero motion |

Removed runs (superseded or intermediate) are in git: commits 1648fcf (v1 true-start systems, old 3D pages), 52d7892 (intermediate training runs, v1 / no-recovery systems, augmentation), 870a144 (v1 SCR-only runs `sys-scronly-*`), 50ef6f5 (hybrid-system 3D pages `volume3d-final`); their numbers are in the earlier summary (commit 870a144).
