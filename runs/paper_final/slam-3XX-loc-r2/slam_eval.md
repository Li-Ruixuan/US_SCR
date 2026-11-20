# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.6 mm, 0.62 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.6 / 8.5 | 2.2 | 0.22 | 2.1 / 5.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.15 | 2.82 | 100 % | 0.56 |
| run-314 | 1.27 | 1.89 | 100 % | 0.44 |
| run-315 | 1.46 | 3.04 | 100 % | 0.92 |
| run-316 | 1.36 | 2.30 | 100 % | 0.80 |
| run-317 | 1.96 | 4.15 | 100 % | 1.11 |
| **mean** | **1.64** | 2.84 | 100 % | 0.77 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-3XX-loc-r2/poses/*.json --out runs/paper_final/slam-3XX-loc-r2/shape.md`
