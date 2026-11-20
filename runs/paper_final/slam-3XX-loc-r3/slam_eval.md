# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.7 mm, 0.60 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 8.6 | 2.2 | 0.21 | 2.1 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.61 | 3.13 | 100 % | 0.56 |
| run-314 | 1.20 | 1.83 | 100 % | 0.43 |
| run-315 | 1.60 | 3.18 | 100 % | 0.93 |
| run-316 | 1.29 | 2.33 | 100 % | 0.78 |
| run-317 | 2.08 | 3.33 | 100 % | 1.09 |
| **mean** | **1.76** | 2.76 | 100 % | 0.76 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-3XX-loc-r3/poses/*.json --out runs/paper_final/slam-3XX-loc-r3/shape.md`
