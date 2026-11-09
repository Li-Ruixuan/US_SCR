# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.8 | 0.24 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.27 | 8.13 | 100 % | 0.66 |
| run-530 | 5.35 | 8.11 | 100 % | 0.66 |
| run-531 | 5.51 | 13.32 | 100 % | 0.98 |
| run-532 | 3.64 | 10.90 | 100 % | 0.71 |
| **mean** | **4.19** | 10.11 | 100 % | 0.75 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-oldC-loc/poses/*.json --out runs/slam-5XXE-oldC-loc/shape.md`
