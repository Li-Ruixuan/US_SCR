# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.7 mm, 0.60 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 8.6 | 2.2 | 0.21 | 2.1 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.61 | 3.12 | 100 % | 0.50 |
| run-314 | 1.20 | 1.85 | 100 % | 0.39 |
| run-315 | 1.57 | 3.07 | 100 % | 0.88 |
| run-316 | 1.28 | 2.23 | 100 % | 0.62 |
| run-317 | 2.07 | 3.31 | 100 % | 1.02 |
| **mean** | **1.74** | 2.72 | 100 % | 0.68 |

Shape: `python tools/us_analysis.py shape --json runs/slam-3XX-loc-r3/poses/*.json --out runs/slam-3XX-loc-r3/shape.md`
