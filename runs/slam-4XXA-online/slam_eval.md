# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.1 / 11.6 | 5.4 | 0.35 | 4.2 / 10.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 5.67 | 6.99 | 100 % | 1.07 |
| run-402 | 3.06 | 4.69 | 100 % | 0.49 |
| run-403 | 4.05 | 4.44 | 100 % | 0.44 |
| run-404 | 3.76 | 4.27 | 100 % | 0.51 |
| run-405 | 3.46 | 5.39 | 100 % | 0.74 |
| run-406 | 5.68 | 6.17 | 100 % | 0.51 |
| run-407 | 5.22 | 6.16 | 100 % | 0.70 |
| run-408 | 5.16 | 5.98 | 100 % | 0.66 |
| **mean** | **4.51** | 5.51 | 100 % | 0.64 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXA-online/poses/*.json --out runs/slam-4XXA-online/shape.md`
