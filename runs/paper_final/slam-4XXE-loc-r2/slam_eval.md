# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.2 | 3.3 | 0.25 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.47 | 5.40 | 100 % | 1.25 |
| run-426 | 4.60 | 47.57 | 100 % | 1.56 |
| run-427 | 6.65 | 15.08 | 100 % | 1.00 |
| run-428 | 3.96 | 6.47 | 100 % | 0.74 |
| **mean** | **4.92** | 18.63 | 100 % | 1.14 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXE-loc-r2/poses/*.json --out runs/paper_final/slam-4XXE-loc-r2/shape.md`
