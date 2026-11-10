# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ60-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.0 | 0.24 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.53 | 6.64 | 100 % | 0.69 |
| run-518 | 2.80 | 6.14 | 100 % | 0.52 |
| run-519 | 2.70 | 13.48 | 100 % | 1.31 |
| run-520 | 2.17 | 7.88 | 100 % | 1.17 |
| run-521 | 3.08 | 8.25 | 100 % | 0.76 |
| run-522 | 2.81 | 11.28 | 100 % | 0.68 |
| run-523 | 2.87 | 6.78 | 100 % | 1.15 |
| run-524 | 2.27 | 5.64 | 100 % | 0.92 |
| **mean** | **2.65** | 8.26 | 100 % | 0.90 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ60-loc/poses/*.json --out runs/slam-5XXC-exam-occ60-loc/shape.md`
