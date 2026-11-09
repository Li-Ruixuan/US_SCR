# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-loc/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 10.0 mm, 0.59 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 8.5 | 2.2 | 0.22 | 2.1 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.60 | 2.96 | 100 % | 0.49 |
| run-314 | 1.50 | 2.09 | 100 % | 0.40 |
| run-315 | 1.67 | 3.58 | 100 % | 0.87 |
| run-316 | 1.33 | 2.22 | 100 % | 0.60 |
| run-317 | 2.12 | 4.14 | 100 % | 1.05 |
| **mean** | **1.84** | 3.00 | 100 % | 0.68 |

Shape: `python tools/us_analysis.py shape --json runs/slam-3XX-loc/poses/*.json --out runs/slam-3XX-loc/shape.md`
