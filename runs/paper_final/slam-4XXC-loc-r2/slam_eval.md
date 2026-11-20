# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.1 | 0.24 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 3.76 | 4.53 | 100 % | 0.58 |
| run-414 | 5.31 | 7.39 | 100 % | 0.63 |
| run-415 | 3.85 | 4.57 | 100 % | 0.52 |
| run-416 | 4.22 | 5.99 | 100 % | 0.74 |
| **mean** | **4.28** | 5.62 | 100 % | 0.62 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXC-loc-r2/poses/*.json --out runs/paper_final/slam-4XXC-loc-r2/shape.md`
