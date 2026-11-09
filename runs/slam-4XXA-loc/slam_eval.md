# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.2 / 11.6 | 5.0 | 0.33 | 4.0 / 9.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 5.09 | 6.96 | 100 % | 1.08 |
| run-402 | 3.03 | 4.63 | 100 % | 0.56 |
| run-403 | 3.98 | 4.51 | 100 % | 0.51 |
| run-404 | 3.53 | 4.23 | 100 % | 0.64 |
| run-405 | 3.23 | 5.21 | 100 % | 0.83 |
| run-406 | 6.36 | 7.09 | 100 % | 0.57 |
| run-407 | 5.06 | 6.50 | 100 % | 0.78 |
| run-408 | 5.47 | 6.97 | 100 % | 0.85 |
| **mean** | **4.47** | 5.76 | 100 % | 0.73 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXA-loc/poses/*.json --out runs/slam-4XXA-loc/shape.md`
