# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.0 | 0.24 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 4.22 | 5.12 | 100 % | 0.58 |
| run-414 | 5.71 | 7.67 | 100 % | 0.61 |
| run-415 | 4.73 | 5.28 | 100 % | 0.53 |
| run-416 | 4.98 | 6.65 | 100 % | 0.72 |
| **mean** | **4.91** | 6.18 | 100 % | 0.61 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXC-loc/poses/*.json --out runs/paper_final/slam-4XXC-loc/shape.md`
