# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ30-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.0 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.33 | 3.04 | 100 % | 0.42 |
| run-518 | 2.61 | 3.40 | 100 % | 0.38 |
| run-519 | 2.47 | 3.54 | 100 % | 0.47 |
| run-520 | 2.13 | 4.89 | 100 % | 0.64 |
| run-521 | 2.90 | 3.92 | 100 % | 0.46 |
| run-522 | 2.62 | 3.79 | 100 % | 0.42 |
| run-523 | 2.45 | 4.27 | 100 % | 0.73 |
| run-524 | 2.20 | 3.38 | 100 % | 0.49 |
| **mean** | **2.46** | 3.78 | 100 % | 0.50 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-occ30-loc/poses/*.json --out runs/paper_final/slam-5XXC-exam-occ30-loc/shape.md`
