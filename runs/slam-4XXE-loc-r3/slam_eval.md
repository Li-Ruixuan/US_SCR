# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.1 | 3.4 | 0.25 | 2.1 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.23 | 5.29 | 100 % | 1.00 |
| run-426 | 28.24 | 62.70 | 100 % | 1.51 |
| run-427 | 7.34 | 17.09 | 100 % | 0.98 |
| run-428 | 3.65 | 6.44 | 100 % | 0.69 |
| **mean** | **10.87** | 22.88 | 100 % | 1.04 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXE-loc-r3/poses/*.json --out runs/slam-4XXE-loc-r3/shape.md`
