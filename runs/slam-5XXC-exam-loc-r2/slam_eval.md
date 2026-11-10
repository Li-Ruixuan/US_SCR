# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.9 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.93 | 2.83 | 100 % | 0.33 |
| run-518 | 2.37 | 3.00 | 100 % | 0.29 |
| run-519 | 2.13 | 2.87 | 100 % | 0.39 |
| run-520 | 1.77 | 3.59 | 100 % | 0.57 |
| run-521 | 2.49 | 3.37 | 100 % | 0.40 |
| run-522 | 2.28 | 3.44 | 100 % | 0.37 |
| run-523 | 2.19 | 3.81 | 100 % | 0.71 |
| run-524 | 1.88 | 3.07 | 100 % | 0.46 |
| **mean** | **2.13** | 3.25 | 100 % | 0.44 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-loc-r2/poses/*.json --out runs/slam-5XXC-exam-loc-r2/shape.md`
