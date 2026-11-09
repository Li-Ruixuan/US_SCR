# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.29 | 2.45 | 100 % | 0.49 |
| run-510 | 1.71 | 2.49 | 100 % | 0.41 |
| run-511 | 1.43 | 2.21 | 100 % | 0.32 |
| run-512 | 2.80 | 3.85 | 100 % | 0.53 |
| run-513 | 1.23 | 2.46 | 100 % | 0.42 |
| run-514 | 1.44 | 2.72 | 100 % | 0.63 |
| run-515 | 1.90 | 2.92 | 100 % | 0.47 |
| run-516 | 1.77 | 3.21 | 100 % | 0.61 |
| **mean** | **1.70** | 2.79 | 100 % | 0.49 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-loc/poses/*.json --out runs/slam-5XXB-exam-loc/shape.md`
