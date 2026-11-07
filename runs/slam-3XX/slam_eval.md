# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.4 mm, 0.61 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.6 / 8.6 | 2.2 | 0.21 | 2.3 / 5.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.70 | 3.18 | 100 % | 0.55 |
| run-314 | 1.23 | 1.74 | 100 % | 0.41 |
| run-315 | 1.58 | 3.61 | 100 % | 0.98 |
| run-316 | 1.11 | 2.32 | 100 % | 0.66 |
| run-317 | 2.35 | 4.33 | 100 % | 1.06 |
| **mean** | **1.79** | 3.04 | 100 % | 0.73 |

Shape: `python tools/us_analysis.py shape --json runs/slam-3XX/poses/*.json --out runs/slam-3XX/shape.md`
