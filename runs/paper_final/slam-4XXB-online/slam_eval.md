# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 6.7 | 3.1 | 0.25 | 1.9 / 4.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 1.93 | 2.92 | 100 % | 0.82 |
| run-410 | 4.09 | 48.74 | 100 % | 0.93 |
| run-411 | 3.41 | 4.20 | 100 % | 0.65 |
| run-412 | 3.92 | 4.73 | 100 % | 0.67 |
| **mean** | **3.34** | 15.15 | 100 % | 0.77 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXB-online/poses/*.json --out runs/paper_final/slam-4XXB-online/shape.md`
