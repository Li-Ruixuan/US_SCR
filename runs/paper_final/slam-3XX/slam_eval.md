# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.4 mm, 0.61 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.6 / 8.6 | 2.2 | 0.21 | 2.3 / 5.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.74 | 3.18 | 100 % | 0.60 |
| run-314 | 1.18 | 1.75 | 100 % | 0.44 |
| run-315 | 1.62 | 3.68 | 100 % | 1.02 |
| run-316 | 1.16 | 2.39 | 100 % | 0.80 |
| run-317 | 2.32 | 4.58 | 100 % | 1.14 |
| **mean** | **1.80** | 3.12 | 100 % | 0.80 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-3XX/poses/*.json --out runs/paper_final/slam-3XX/shape.md`
