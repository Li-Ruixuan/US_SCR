# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.1 | 0.24 | 2.0 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 4.13 | 4.93 | 100 % | 0.58 |
| run-414 | 5.63 | 7.66 | 100 % | 0.62 |
| run-415 | 4.38 | 4.93 | 100 % | 0.52 |
| run-416 | 4.37 | 6.00 | 100 % | 0.70 |
| **mean** | **4.63** | 5.88 | 100 % | 0.61 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXC-loc-r3/poses/*.json --out runs/paper_final/slam-4XXC-loc-r3/shape.md`
