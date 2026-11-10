# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ30-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.0 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.36 | 3.07 | 100 % | 0.46 |
| run-518 | 2.63 | 3.41 | 100 % | 0.42 |
| run-519 | 2.46 | 3.63 | 100 % | 0.53 |
| run-520 | 2.11 | 4.98 | 100 % | 0.75 |
| run-521 | 2.90 | 3.92 | 100 % | 0.52 |
| run-522 | 2.64 | 3.79 | 100 % | 0.45 |
| run-523 | 2.46 | 4.28 | 100 % | 0.81 |
| run-524 | 2.26 | 3.41 | 100 % | 0.56 |
| **mean** | **2.48** | 3.81 | 100 % | 0.56 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ30-loc/poses/*.json --out runs/slam-5XXC-exam-occ30-loc/shape.md`
