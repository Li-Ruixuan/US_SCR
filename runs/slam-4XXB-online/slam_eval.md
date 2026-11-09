# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 29 % | 3.7 / 6.4 | 3.6 | 0.24 | 1.9 / 4.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | nan | nan | 0 % | nan |
| run-410 | nan | nan | 0 % | nan |
| run-411 | nan | nan | 0 % | nan |
| run-412 | nan | nan | 0 % | nan |
| **mean** | **nan** | nan | 0 % | nan |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXB-online/poses/*.json --out runs/slam-4XXB-online/shape.md`
