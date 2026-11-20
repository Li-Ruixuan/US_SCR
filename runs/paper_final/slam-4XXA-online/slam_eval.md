# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.1 / 11.6 | 5.4 | 0.35 | 4.2 / 10.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 5.66 | 7.05 | 100 % | 1.31 |
| run-402 | 3.08 | 4.80 | 100 % | 0.60 |
| run-403 | 4.06 | 4.44 | 100 % | 0.45 |
| run-404 | 3.78 | 4.30 | 100 % | 0.61 |
| run-405 | 3.44 | 5.33 | 100 % | 0.82 |
| run-406 | 5.67 | 6.17 | 100 % | 0.56 |
| run-407 | 5.19 | 6.19 | 100 % | 0.70 |
| run-408 | 5.16 | 5.97 | 100 % | 0.62 |
| **mean** | **4.50** | 5.53 | 100 % | 0.71 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXA-online/poses/*.json --out runs/paper_final/slam-4XXA-online/shape.md`
