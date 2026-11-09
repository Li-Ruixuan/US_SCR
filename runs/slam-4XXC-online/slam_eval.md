# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.1 | 3.2 | 0.24 | 2.0 / 5.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 6.12 | 33.15 | 100 % | 0.84 |
| run-414 | 6.12 | 8.07 | 100 % | 0.58 |
| run-415 | 4.75 | 5.42 | 100 % | 0.44 |
| run-416 | 4.87 | 5.57 | 100 % | 0.50 |
| **mean** | **5.47** | 13.05 | 100 % | 0.59 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXC-online/poses/*.json --out runs/slam-4XXC-online/shape.md`
