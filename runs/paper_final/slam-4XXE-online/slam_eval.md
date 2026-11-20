# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.24 | 2.0 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.45 | 5.58 | 100 % | 1.25 |
| run-426 | 3.76 | 4.85 | 100 % | 1.12 |
| run-427 | 6.08 | 7.65 | 100 % | 0.81 |
| run-428 | 3.42 | 5.88 | 100 % | 0.75 |
| **mean** | **4.43** | 5.99 | 100 % | 0.98 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXE-online/poses/*.json --out runs/paper_final/slam-4XXE-online/shape.md`
