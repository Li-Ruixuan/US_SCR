# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-reloc/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.8 mm, 0.59 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.6 / 8.5 | 2.2 | 0.22 | 2.2 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.39 | 2.88 | 100 % | 0.58 |
| run-314 | 1.36 | 2.01 | 100 % | 0.45 |
| run-315 | 1.67 | 3.48 | 100 % | 0.98 |
| run-316 | 1.17 | 2.12 | 100 % | 0.80 |
| run-317 | 2.12 | 5.21 | 100 % | 1.12 |
| **mean** | **1.74** | 3.14 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-3XX-reloc/poses/*.json --out runs/paper_final/slam-3XX-reloc/shape.md`
