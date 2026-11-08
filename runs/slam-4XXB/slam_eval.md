# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.5 / 6.6 | 2.8 | 0.23 | 1.9 / 4.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 1.49 | 2.62 | 100 % | 0.75 |
| run-410 | 3.56 | 4.23 | 100 % | 0.68 |
| run-411 | 3.26 | 3.82 | 100 % | 0.71 |
| run-412 | 3.65 | 4.81 | 100 % | 0.78 |
| **mean** | **2.99** | 3.87 | 100 % | 0.73 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXB/poses/*.json --out runs/slam-4XXB/shape.md`
