# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.1 / 11.5 | 5.2 | 0.33 | 4.3 / 10.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 4.80 | 6.79 | 100 % | 1.18 |
| run-402 | 4.81 | 5.93 | 100 % | 0.64 |
| run-403 | 3.51 | 4.08 | 100 % | 0.48 |
| run-404 | 3.75 | 4.37 | 100 % | 0.57 |
| run-405 | 3.50 | 5.24 | 100 % | 0.80 |
| run-406 | 5.58 | 6.19 | 100 % | 0.60 |
| run-407 | 4.84 | 6.58 | 100 % | 0.74 |
| run-408 | 4.78 | 5.83 | 100 % | 0.74 |
| **mean** | **4.45** | 5.63 | 100 % | 0.72 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXA/poses/*.json --out runs/slam-4XXA/shape.md`
