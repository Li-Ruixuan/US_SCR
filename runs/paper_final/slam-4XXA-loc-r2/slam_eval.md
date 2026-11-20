# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.2 / 11.6 | 5.0 | 0.33 | 4.0 / 10.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 4.52 | 6.02 | 100 % | 1.32 |
| run-402 | 3.23 | 4.27 | 100 % | 0.63 |
| run-403 | 3.43 | 3.85 | 100 % | 0.46 |
| run-404 | 3.18 | 3.78 | 100 % | 0.68 |
| run-405 | 2.87 | 4.56 | 100 % | 0.88 |
| run-406 | 5.79 | 6.80 | 100 % | 0.58 |
| run-407 | 4.24 | 5.87 | 100 % | 0.74 |
| run-408 | 4.81 | 6.68 | 100 % | 0.71 |
| **mean** | **4.01** | 5.23 | 100 % | 0.75 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXA-loc-r2/poses/*.json --out runs/paper_final/slam-4XXA-loc-r2/shape.md`
