# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.08 | 3.90 | 100 % | 0.42 |
| run-530 | 3.63 | 4.53 | 100 % | 0.33 |
| run-531 | 3.22 | 4.95 | 100 % | 0.51 |
| run-532 | 2.37 | 3.30 | 100 % | 0.42 |
| **mean** | **2.82** | 4.17 | 100 % | 0.42 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-oldC-online/poses/*.json --out runs/paper_final/slam-5XXE-oldC-online/shape.md`
