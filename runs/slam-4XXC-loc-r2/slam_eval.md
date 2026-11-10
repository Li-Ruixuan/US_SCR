# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.1 | 0.24 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 3.77 | 4.50 | 100 % | 0.57 |
| run-414 | 5.30 | 7.45 | 100 % | 0.64 |
| run-415 | 3.82 | 4.61 | 100 % | 0.50 |
| run-416 | 4.18 | 5.94 | 100 % | 0.66 |
| **mean** | **4.27** | 5.63 | 100 % | 0.59 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXC-loc-r2/poses/*.json --out runs/slam-4XXC-loc-r2/shape.md`
