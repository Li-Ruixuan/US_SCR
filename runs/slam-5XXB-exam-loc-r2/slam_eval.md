# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.41 | 2.59 | 100 % | 0.49 |
| run-510 | 1.81 | 2.54 | 100 % | 0.43 |
| run-511 | 1.23 | 2.22 | 100 % | 0.34 |
| run-512 | 2.82 | 3.86 | 100 % | 0.58 |
| run-513 | 1.08 | 2.51 | 100 % | 0.42 |
| run-514 | 1.36 | 2.71 | 100 % | 0.64 |
| run-515 | 1.96 | 2.98 | 100 % | 0.48 |
| run-516 | 1.62 | 3.00 | 100 % | 0.62 |
| **mean** | **1.66** | 2.80 | 100 % | 0.50 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-loc-r2/poses/*.json --out runs/slam-5XXB-exam-loc-r2/shape.md`
