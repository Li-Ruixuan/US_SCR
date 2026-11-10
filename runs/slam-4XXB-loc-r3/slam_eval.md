# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 6.7 | 3.2 | 0.25 | 1.9 / 4.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 1.90 | 2.97 | 100 % | 0.69 |
| run-410 | 4.15 | 4.78 | 100 % | 0.64 |
| run-411 | 3.65 | 4.43 | 100 % | 0.72 |
| run-412 | 4.05 | 5.29 | 100 % | 0.74 |
| **mean** | **3.44** | 4.37 | 100 % | 0.70 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXB-loc-r3/poses/*.json --out runs/slam-4XXB-loc-r3/shape.md`
