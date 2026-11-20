# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 6.8 | 3.5 | 0.26 | 1.9 / 4.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 2.10 | 3.59 | 100 % | 0.84 |
| run-410 | 4.33 | 5.05 | 100 % | 0.65 |
| run-411 | 3.89 | 4.74 | 100 % | 0.67 |
| run-412 | 4.43 | 5.79 | 100 % | 0.66 |
| **mean** | **3.69** | 4.79 | 100 % | 0.70 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXB-loc-r2/poses/*.json --out runs/paper_final/slam-4XXB-loc-r2/shape.md`
