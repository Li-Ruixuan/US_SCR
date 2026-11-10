# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.24 | 2.1 / 5.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 3.75 | 5.37 | 100 % | 0.64 |
| run-419 | 3.36 | 6.93 | 100 % | 0.74 |
| run-420 | 4.09 | 6.83 | 100 % | 0.71 |
| run-421 | 6.19 | 15.80 | 100 % | 0.98 |
| run-423 | 4.12 | 4.68 | 100 % | 0.60 |
| run-424 | 4.11 | 4.60 | 100 % | 0.44 |
| **mean** | **4.27** | 7.37 | 100 % | 0.69 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXD-loc-r3/poses/*.json --out runs/slam-4XXD-loc-r3/shape.md`
