# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.0 | 0.24 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 4.23 | 5.11 | 100 % | 0.57 |
| run-414 | 5.70 | 7.62 | 100 % | 0.62 |
| run-415 | 4.71 | 5.29 | 100 % | 0.54 |
| run-416 | 4.96 | 6.48 | 100 % | 0.63 |
| **mean** | **4.90** | 6.12 | 100 % | 0.59 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXC-loc/poses/*.json --out runs/slam-4XXC-loc/shape.md`
