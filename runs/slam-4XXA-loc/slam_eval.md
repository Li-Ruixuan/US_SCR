# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.1 / 11.5 | 5.1 | 0.34 | 4.1 / 10.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | nan | nan | 0 % | nan |
| run-402 | nan | nan | 0 % | nan |
| run-403 | nan | nan | 0 % | nan |
| run-404 | nan | nan | 0 % | nan |
| run-405 | nan | nan | 0 % | nan |
| run-406 | nan | nan | 0 % | nan |
| run-407 | nan | nan | 0 % | nan |
| run-408 | nan | nan | 0 % | nan |
| **mean** | **nan** | nan | 0 % | nan |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXA-loc/poses/*.json --out runs/slam-4XXA-loc/shape.md`
