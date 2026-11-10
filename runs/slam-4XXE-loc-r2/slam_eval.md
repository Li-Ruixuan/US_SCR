# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.2 | 3.3 | 0.25 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.49 | 5.22 | 100 % | 0.96 |
| run-426 | 4.65 | 47.55 | 100 % | 1.32 |
| run-427 | 6.90 | 14.91 | 100 % | 0.91 |
| run-428 | 3.95 | 6.41 | 100 % | 0.60 |
| **mean** | **5.00** | 18.52 | 100 % | 0.95 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXE-loc-r2/poses/*.json --out runs/slam-4XXE-loc-r2/shape.md`
