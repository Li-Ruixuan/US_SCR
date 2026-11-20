# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.5 | 0.23 | 1.2 / 3.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.47 | 2.28 | 100 % | 0.31 |
| run-518 | 1.88 | 2.52 | 100 % | 0.24 |
| run-519 | 1.53 | 2.23 | 100 % | 0.31 |
| run-520 | 1.88 | 3.25 | 100 % | 0.49 |
| run-521 | 2.02 | 3.07 | 100 % | 0.36 |
| run-522 | 1.85 | 3.05 | 100 % | 0.34 |
| run-523 | 1.93 | 3.62 | 100 % | 0.64 |
| run-524 | 1.98 | 2.85 | 100 % | 0.38 |
| **mean** | **1.82** | 2.86 | 100 % | 0.39 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-loc-r3/poses/*.json --out runs/paper_final/slam-5XXC-exam-loc-r3/shape.md`
