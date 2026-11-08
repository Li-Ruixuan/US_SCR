# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.3 | 2.9 | 0.24 | 2.2 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 2.97 | 5.42 | 100 % | 0.57 |
| run-419 | 2.96 | 4.86 | 100 % | 0.64 |
| run-420 | 4.28 | 5.37 | 100 % | 0.56 |
| run-421 | 4.46 | 6.93 | 100 % | 0.65 |
| run-423 | 3.13 | 4.29 | 100 % | 0.58 |
| run-424 | 3.96 | 4.83 | 100 % | 0.37 |
| **mean** | **3.63** | 5.28 | 100 % | 0.56 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXD/poses/*.json --out runs/slam-4XXD/shape.md`
