# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.2 / 11.6 | 5.0 | 0.33 | 4.0 / 10.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 4.50 | 5.95 | 100 % | 1.07 |
| run-402 | 3.23 | 4.24 | 100 % | 0.56 |
| run-403 | 3.42 | 3.87 | 100 % | 0.49 |
| run-404 | 3.19 | 3.79 | 100 % | 0.66 |
| run-405 | 2.90 | 4.50 | 100 % | 0.86 |
| run-406 | 5.79 | 6.82 | 100 % | 0.56 |
| run-407 | 4.38 | 5.85 | 100 % | 0.77 |
| run-408 | 4.82 | 6.68 | 100 % | 0.82 |
| **mean** | **4.03** | 5.21 | 100 % | 0.72 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXA-loc-r2/poses/*.json --out runs/slam-4XXA-loc-r2/shape.md`
