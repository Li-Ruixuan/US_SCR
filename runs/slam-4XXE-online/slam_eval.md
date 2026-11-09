# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.24 | 2.0 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.41 | 5.48 | 100 % | 0.98 |
| run-426 | 3.69 | 4.85 | 100 % | 0.82 |
| run-427 | 6.07 | 7.58 | 100 % | 0.66 |
| run-428 | 3.38 | 5.80 | 100 % | 0.61 |
| **mean** | **4.39** | 5.93 | 100 % | 0.77 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXE-online/poses/*.json --out runs/slam-4XXE-online/shape.md`
