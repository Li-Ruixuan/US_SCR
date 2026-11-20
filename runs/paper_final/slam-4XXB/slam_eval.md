# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.5 / 6.6 | 2.8 | 0.23 | 1.9 / 4.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 1.54 | 2.66 | 100 % | 0.83 |
| run-410 | 3.58 | 4.26 | 100 % | 0.66 |
| run-411 | 3.25 | 3.83 | 100 % | 0.67 |
| run-412 | 3.68 | 4.71 | 100 % | 0.71 |
| **mean** | **3.01** | 3.86 | 100 % | 0.72 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXB/poses/*.json --out runs/paper_final/slam-4XXB/shape.md`
