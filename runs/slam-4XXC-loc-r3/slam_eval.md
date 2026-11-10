# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.1 | 0.24 | 2.0 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 4.16 | 4.87 | 100 % | 0.56 |
| run-414 | 5.60 | 7.63 | 100 % | 0.63 |
| run-415 | 4.37 | 4.95 | 100 % | 0.49 |
| run-416 | 4.41 | 6.04 | 100 % | 0.59 |
| **mean** | **4.63** | 5.87 | 100 % | 0.57 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXC-loc-r3/poses/*.json --out runs/slam-4XXC-loc-r3/shape.md`
