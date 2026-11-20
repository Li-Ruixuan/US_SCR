# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.1 | 3.2 | 0.24 | 2.0 / 5.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 6.13 | 33.15 | 100 % | 0.85 |
| run-414 | 6.17 | 8.10 | 100 % | 0.60 |
| run-415 | 4.76 | 5.44 | 100 % | 0.50 |
| run-416 | 4.87 | 5.63 | 100 % | 0.63 |
| **mean** | **5.48** | 13.08 | 100 % | 0.64 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXC-online/poses/*.json --out runs/paper_final/slam-4XXC-online/shape.md`
