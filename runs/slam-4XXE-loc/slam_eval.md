# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.2 | 3.2 | 0.24 | 2.1 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.03 | 5.12 | 100 % | 0.97 |
| run-426 | 81.54 | 96.69 | 100 % | 1.87 |
| run-427 | 6.84 | 16.87 | 100 % | 0.90 |
| run-428 | 3.69 | 6.02 | 100 % | 0.59 |
| **mean** | **24.03** | 31.18 | 100 % | 1.08 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXE-loc/poses/*.json --out runs/slam-4XXE-loc/shape.md`
