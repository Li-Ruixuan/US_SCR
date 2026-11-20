# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.2 / 11.6 | 5.4 | 0.35 | 4.1 / 10.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 5.61 | 7.47 | 100 % | 1.32 |
| run-402 | 3.73 | 5.59 | 100 % | 0.61 |
| run-403 | 4.23 | 4.99 | 100 % | 0.47 |
| run-404 | 3.82 | 4.35 | 100 % | 0.64 |
| run-405 | 3.66 | 4.78 | 100 % | 0.87 |
| run-406 | 7.25 | 8.08 | 100 % | 0.59 |
| run-407 | 5.42 | 7.07 | 100 % | 0.74 |
| run-408 | 5.94 | 8.00 | 100 % | 0.70 |
| **mean** | **4.96** | 6.29 | 100 % | 0.74 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXA-loc-r3/poses/*.json --out runs/paper_final/slam-4XXA-loc-r3/shape.md`
