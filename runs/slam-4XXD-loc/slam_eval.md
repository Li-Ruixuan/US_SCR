# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.1 | 3.2 | 0.24 | 2.0 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | nan | nan | 0 % | nan |
| run-419 | nan | nan | 0 % | nan |
| run-420 | nan | nan | 0 % | nan |
| run-421 | nan | nan | 0 % | nan |
| run-423 | nan | nan | 0 % | nan |
| run-424 | nan | nan | 0 % | nan |
| **mean** | **nan** | nan | 0 % | nan |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXD-loc/poses/*.json --out runs/slam-4XXD-loc/shape.md`
