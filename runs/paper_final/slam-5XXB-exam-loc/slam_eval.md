# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.30 | 2.48 | 100 % | 0.52 |
| run-510 | 1.74 | 2.44 | 100 % | 0.38 |
| run-511 | 1.41 | 2.20 | 100 % | 0.31 |
| run-512 | 2.76 | 3.83 | 100 % | 0.46 |
| run-513 | 1.22 | 2.49 | 100 % | 0.41 |
| run-514 | 1.46 | 2.70 | 100 % | 0.65 |
| run-515 | 1.88 | 2.93 | 100 % | 0.46 |
| run-516 | 1.79 | 3.21 | 100 % | 0.59 |
| **mean** | **1.70** | 2.79 | 100 % | 0.47 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-loc/poses/*.json --out runs/paper_final/slam-5XXB-exam-loc/shape.md`
