# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.25 | 2.0 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.13 | 5.57 | 100 % | 0.65 |
| run-419 | 3.58 | 6.28 | 100 % | 0.74 |
| run-420 | 4.94 | 6.48 | 100 % | 0.65 |
| run-421 | 5.91 | 15.20 | 100 % | 0.95 |
| run-423 | 4.70 | 5.59 | 100 % | 0.69 |
| run-424 | 4.59 | 5.26 | 100 % | 0.49 |
| **mean** | **4.64** | 7.40 | 100 % | 0.69 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXD-loc/poses/*.json --out runs/slam-4XXD-loc/shape.md`
