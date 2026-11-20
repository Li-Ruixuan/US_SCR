# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-loc/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 10.0 mm, 0.59 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 8.5 | 2.2 | 0.22 | 2.1 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.60 | 2.96 | 100 % | 0.56 |
| run-314 | 1.51 | 2.14 | 100 % | 0.43 |
| run-315 | 1.70 | 3.62 | 100 % | 0.93 |
| run-316 | 1.36 | 2.23 | 100 % | 0.77 |
| run-317 | 2.07 | 3.98 | 100 % | 1.09 |
| **mean** | **1.85** | 2.99 | 100 % | 0.75 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-3XX-loc/poses/*.json --out runs/paper_final/slam-3XX-loc/shape.md`
