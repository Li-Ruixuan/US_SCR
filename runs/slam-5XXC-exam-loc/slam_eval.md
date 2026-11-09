# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.5 | 0.22 | 1.3 / 3.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.02 | 2.78 | 100 % | 0.33 |
| run-518 | 2.05 | 2.86 | 100 % | 0.29 |
| run-519 | 1.79 | 2.70 | 100 % | 0.37 |
| run-520 | 2.08 | 3.46 | 100 % | 0.57 |
| run-521 | 2.24 | 3.40 | 100 % | 0.39 |
| run-522 | 2.04 | 3.23 | 100 % | 0.37 |
| run-523 | 1.99 | 3.80 | 100 % | 0.69 |
| run-524 | 2.15 | 3.27 | 100 % | 0.46 |
| **mean** | **2.05** | 3.19 | 100 % | 0.43 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-loc/poses/*.json --out runs/slam-5XXC-exam-loc/shape.md`
