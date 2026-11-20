# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 6.7 | 3.4 | 0.26 | 1.9 / 4.6 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 2.33 | 3.36 | 100 % | 0.83 |
| run-410 | 4.27 | 4.97 | 100 % | 0.63 |
| run-411 | 3.95 | 4.74 | 100 % | 0.67 |
| run-412 | 4.66 | 5.81 | 100 % | 0.69 |
| **mean** | **3.80** | 4.72 | 100 % | 0.70 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXB-loc/poses/*.json --out runs/paper_final/slam-4XXB-loc/shape.md`
