# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.4 | 2.9 | 0.24 | 2.2 / 5.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 2.70 | 3.51 | 100 % | 0.57 |
| run-414 | 4.73 | 6.04 | 100 % | 0.64 |
| run-415 | 3.77 | 4.25 | 100 % | 0.54 |
| run-416 | 3.31 | 4.46 | 100 % | 0.64 |
| **mean** | **3.63** | 4.56 | 100 % | 0.60 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXC/poses/*.json --out runs/paper_final/slam-4XXC/shape.md`
