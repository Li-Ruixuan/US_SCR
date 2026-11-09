# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-online/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 10.1 mm, 0.60 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 8.5 | 2.2 | 0.22 | 2.1 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.50 | 3.03 | 100 % | 0.48 |
| run-314 | 1.43 | 2.12 | 100 % | 0.41 |
| run-315 | 1.54 | 3.41 | 100 % | 0.88 |
| run-316 | 1.55 | 2.16 | 100 % | 0.63 |
| run-317 | 2.03 | 3.72 | 100 % | 0.95 |
| **mean** | **1.81** | 2.89 | 100 % | 0.67 |

Shape: `python tools/us_analysis.py shape --json runs/slam-3XX-online/poses/*.json --out runs/slam-3XX-online/shape.md`
