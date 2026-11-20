# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.5 | 0.22 | 1.3 / 3.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.02 | 2.79 | 100 % | 0.31 |
| run-518 | 2.04 | 2.85 | 100 % | 0.25 |
| run-519 | 1.78 | 2.68 | 100 % | 0.32 |
| run-520 | 2.08 | 3.46 | 100 % | 0.49 |
| run-521 | 2.22 | 3.41 | 100 % | 0.37 |
| run-522 | 2.01 | 3.22 | 100 % | 0.34 |
| run-523 | 1.99 | 3.79 | 100 % | 0.64 |
| run-524 | 2.14 | 3.22 | 100 % | 0.40 |
| **mean** | **2.04** | 3.18 | 100 % | 0.39 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-loc/poses/*.json --out runs/paper_final/slam-5XXC-exam-loc/shape.md`
