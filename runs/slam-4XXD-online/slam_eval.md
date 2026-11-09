# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.24 | 2.0 / 5.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.87 | 6.44 | 100 % | 0.57 |
| run-419 | 4.15 | 6.04 | 100 % | 0.58 |
| run-420 | 5.24 | 6.52 | 100 % | 0.50 |
| run-421 | 5.11 | 7.99 | 100 % | 0.65 |
| run-423 | 4.27 | 4.85 | 100 % | 0.54 |
| run-424 | 4.47 | 5.47 | 100 % | 0.34 |
| **mean** | **4.69** | 6.22 | 100 % | 0.53 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXD-online/poses/*.json --out runs/slam-4XXD-online/shape.md`
