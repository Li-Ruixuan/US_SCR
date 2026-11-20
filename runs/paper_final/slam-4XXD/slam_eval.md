# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.3 | 2.9 | 0.24 | 2.2 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 2.97 | 5.50 | 100 % | 0.63 |
| run-419 | 2.93 | 4.94 | 100 % | 0.83 |
| run-420 | 4.33 | 5.34 | 100 % | 0.65 |
| run-421 | 4.52 | 6.91 | 100 % | 0.90 |
| run-423 | 3.13 | 4.26 | 100 % | 0.72 |
| run-424 | 3.93 | 4.86 | 100 % | 0.46 |
| **mean** | **3.64** | 5.30 | 100 % | 0.70 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXD/poses/*.json --out runs/paper_final/slam-4XXD/shape.md`
