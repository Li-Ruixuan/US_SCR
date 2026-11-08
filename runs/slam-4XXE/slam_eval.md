# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.3 | 2.6 | 0.23 | 2.3 / 5.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 3.15 | 5.05 | 100 % | 0.99 |
| run-426 | 2.69 | 3.48 | 100 % | 0.85 |
| run-427 | 4.04 | 6.10 | 100 % | 0.65 |
| run-428 | 2.30 | 4.33 | 100 % | 0.62 |
| **mean** | **3.04** | 4.74 | 100 % | 0.78 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXE/poses/*.json --out runs/slam-4XXE/shape.md`
