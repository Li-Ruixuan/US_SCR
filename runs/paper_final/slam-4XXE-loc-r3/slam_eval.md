# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.1 | 3.4 | 0.25 | 2.1 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.24 | 5.42 | 100 % | 1.27 |
| run-426 | 25.40 | 62.67 | 100 % | 1.71 |
| run-427 | 7.29 | 17.18 | 100 % | 1.08 |
| run-428 | 3.68 | 6.52 | 100 % | 0.80 |
| **mean** | **10.15** | 22.95 | 100 % | 1.21 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXE-loc-r3/poses/*.json --out runs/paper_final/slam-4XXE-loc-r3/shape.md`
