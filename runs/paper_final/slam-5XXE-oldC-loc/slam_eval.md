# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.8 | 0.24 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.28 | 8.19 | 100 % | 0.52 |
| run-530 | 5.35 | 8.07 | 100 % | 0.56 |
| run-531 | 5.53 | 13.14 | 100 % | 0.97 |
| run-532 | 3.65 | 10.87 | 100 % | 0.59 |
| **mean** | **4.20** | 10.07 | 100 % | 0.66 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-oldC-loc/poses/*.json --out runs/paper_final/slam-5XXE-oldC-loc/shape.md`
