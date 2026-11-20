# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.24 | 2.1 / 5.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 3.75 | 5.37 | 100 % | 0.73 |
| run-419 | 3.31 | 6.87 | 100 % | 0.91 |
| run-420 | 4.11 | 6.85 | 100 % | 0.74 |
| run-421 | 6.23 | 15.72 | 100 % | 1.15 |
| run-423 | 4.13 | 4.63 | 100 % | 0.72 |
| run-424 | 4.11 | 4.57 | 100 % | 0.47 |
| **mean** | **4.27** | 7.33 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXD-loc-r3/poses/*.json --out runs/paper_final/slam-4XXD-loc-r3/shape.md`
