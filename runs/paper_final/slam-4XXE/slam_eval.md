# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.3 | 2.6 | 0.23 | 2.3 / 5.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 3.19 | 5.01 | 100 % | 1.28 |
| run-426 | 2.76 | 3.49 | 100 % | 1.14 |
| run-427 | 4.01 | 6.04 | 100 % | 0.80 |
| run-428 | 2.35 | 4.45 | 100 % | 0.75 |
| **mean** | **3.08** | 4.75 | 100 % | 0.99 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXE/poses/*.json --out runs/paper_final/slam-4XXE/shape.md`
