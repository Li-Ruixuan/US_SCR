# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.6 mm, 0.62 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.6 / 8.5 | 2.2 | 0.22 | 2.1 / 5.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.15 | 2.78 | 100 % | 0.49 |
| run-314 | 1.28 | 1.88 | 100 % | 0.41 |
| run-315 | 1.46 | 3.08 | 100 % | 0.85 |
| run-316 | 1.32 | 2.24 | 100 % | 0.64 |
| run-317 | 1.93 | 4.33 | 100 % | 1.06 |
| **mean** | **1.63** | 2.86 | 100 % | 0.69 |

Shape: `python tools/us_analysis.py shape --json runs/slam-3XX-loc-r2/poses/*.json --out runs/slam-3XX-loc-r2/shape.md`
