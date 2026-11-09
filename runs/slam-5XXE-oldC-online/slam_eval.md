# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.06 | 3.91 | 100 % | 0.44 |
| run-530 | 3.62 | 4.53 | 100 % | 0.35 |
| run-531 | 3.20 | 4.94 | 100 % | 0.42 |
| run-532 | 2.38 | 3.30 | 100 % | 0.44 |
| **mean** | **2.82** | 4.17 | 100 % | 0.41 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-oldC-online/poses/*.json --out runs/slam-5XXE-oldC-online/shape.md`
