# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.2 / 11.6 | 5.0 | 0.33 | 4.0 / 9.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 5.11 | 7.03 | 100 % | 1.32 |
| run-402 | 3.02 | 4.71 | 100 % | 0.63 |
| run-403 | 3.99 | 4.46 | 100 % | 0.47 |
| run-404 | 3.54 | 4.22 | 100 % | 0.65 |
| run-405 | 3.20 | 5.26 | 100 % | 0.87 |
| run-406 | 6.37 | 7.09 | 100 % | 0.59 |
| run-407 | 5.03 | 6.50 | 100 % | 0.74 |
| run-408 | 5.52 | 7.05 | 100 % | 0.72 |
| **mean** | **4.47** | 5.79 | 100 % | 0.75 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXA-loc/poses/*.json --out runs/paper_final/slam-4XXA-loc/shape.md`
