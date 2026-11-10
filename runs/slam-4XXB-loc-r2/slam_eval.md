# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 6.8 | 3.5 | 0.26 | 1.9 / 4.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 2.08 | 3.59 | 100 % | 0.73 |
| run-410 | 4.31 | 5.04 | 100 % | 0.65 |
| run-411 | 3.86 | 4.74 | 100 % | 0.76 |
| run-412 | 4.41 | 5.75 | 100 % | 0.69 |
| **mean** | **3.67** | 4.78 | 100 % | 0.71 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXB-loc-r2/poses/*.json --out runs/slam-4XXB-loc-r2/shape.md`
