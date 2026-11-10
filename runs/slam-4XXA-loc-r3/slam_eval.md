# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.2 / 11.6 | 5.4 | 0.35 | 4.1 / 10.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 5.63 | 7.38 | 100 % | 1.09 |
| run-402 | 3.76 | 5.59 | 100 % | 0.53 |
| run-403 | 4.24 | 4.99 | 100 % | 0.49 |
| run-404 | 3.78 | 4.38 | 100 % | 0.58 |
| run-405 | 3.67 | 4.69 | 100 % | 0.83 |
| run-406 | 7.23 | 8.14 | 100 % | 0.58 |
| run-407 | 5.56 | 7.04 | 100 % | 0.76 |
| run-408 | 5.86 | 7.98 | 100 % | 0.80 |
| **mean** | **4.97** | 6.27 | 100 % | 0.71 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXA-loc-r3/poses/*.json --out runs/slam-4XXA-loc-r3/shape.md`
