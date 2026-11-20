# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.3 / 8.1 | 3.3 | 0.25 | 2.0 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.32 | 5.97 | 100 % | 0.72 |
| run-419 | 3.60 | 6.45 | 100 % | 0.89 |
| run-420 | 4.87 | 6.48 | 100 % | 0.82 |
| run-421 | 6.51 | 14.49 | 100 % | 1.13 |
| run-423 | 4.35 | 5.05 | 100 % | 0.72 |
| run-424 | 4.39 | 4.91 | 100 % | 0.46 |
| **mean** | **4.67** | 7.23 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXD-loc-r2/poses/*.json --out runs/paper_final/slam-4XXD-loc-r2/shape.md`
