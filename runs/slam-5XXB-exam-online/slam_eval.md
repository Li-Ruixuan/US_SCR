# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.6 | 0.22 | 1.2 / 2.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.11 | 2.37 | 100 % | 0.47 |
| run-510 | 1.74 | 2.83 | 100 % | 0.39 |
| run-511 | 1.57 | 2.08 | 100 % | 0.31 |
| run-512 | 3.01 | 4.16 | 100 % | 0.50 |
| run-513 | 1.35 | 2.66 | 100 % | 0.42 |
| run-514 | 1.59 | 2.78 | 100 % | 0.63 |
| run-515 | 2.04 | 3.18 | 100 % | 0.46 |
| run-516 | 1.88 | 3.12 | 100 % | 0.60 |
| **mean** | **1.79** | 2.90 | 100 % | 0.47 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-online/poses/*.json --out runs/slam-5XXB-exam-online/shape.md`
