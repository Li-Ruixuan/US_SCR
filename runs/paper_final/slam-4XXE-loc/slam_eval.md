# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.2 | 3.2 | 0.24 | 2.1 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.07 | 5.36 | 100 % | 1.26 |
| run-426 | 81.59 | 96.67 | 100 % | 1.97 |
| run-427 | 6.61 | 16.86 | 100 % | 1.00 |
| run-428 | 3.72 | 6.21 | 100 % | 0.74 |
| **mean** | **24.00** | 31.28 | 100 % | 1.24 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXE-loc/poses/*.json --out runs/paper_final/slam-4XXE-loc/shape.md`
