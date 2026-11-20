# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.1 / 11.5 | 5.2 | 0.33 | 4.3 / 10.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 4.78 | 6.81 | 100 % | 1.34 |
| run-402 | 4.76 | 5.93 | 100 % | 0.67 |
| run-403 | 3.50 | 4.05 | 100 % | 0.46 |
| run-404 | 3.80 | 4.37 | 100 % | 0.62 |
| run-405 | 3.49 | 5.20 | 100 % | 0.83 |
| run-406 | 5.60 | 6.21 | 100 % | 0.58 |
| run-407 | 4.79 | 6.59 | 100 % | 0.72 |
| run-408 | 4.79 | 5.83 | 100 % | 0.68 |
| **mean** | **4.44** | 5.62 | 100 % | 0.74 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXA/poses/*.json --out runs/paper_final/slam-4XXA/shape.md`
