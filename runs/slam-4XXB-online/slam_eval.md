# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 6.7 | 3.1 | 0.25 | 1.9 / 4.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 1.92 | 2.91 | 100 % | 0.70 |
| run-410 | 4.05 | 49.04 | 100 % | 1.02 |
| run-411 | 3.39 | 4.17 | 100 % | 0.70 |
| run-412 | 3.91 | 4.78 | 100 % | 0.73 |
| **mean** | **3.31** | 15.23 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXB-online/poses/*.json --out runs/slam-4XXB-online/shape.md`
