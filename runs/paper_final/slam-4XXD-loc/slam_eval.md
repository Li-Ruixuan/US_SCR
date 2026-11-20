# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.25 | 2.0 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.12 | 5.59 | 100 % | 0.72 |
| run-419 | 3.61 | 6.31 | 100 % | 0.91 |
| run-420 | 4.95 | 6.47 | 100 % | 0.70 |
| run-421 | 6.01 | 15.24 | 100 % | 1.12 |
| run-423 | 4.67 | 5.62 | 100 % | 0.74 |
| run-424 | 4.58 | 5.25 | 100 % | 0.50 |
| **mean** | **4.66** | 7.41 | 100 % | 0.78 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXD-loc/poses/*.json --out runs/paper_final/slam-4XXD-loc/shape.md`
