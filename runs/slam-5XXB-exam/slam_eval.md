# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.9 | 0.23 | 1.2 / 3.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.66 | 2.31 | 100 % | 0.49 |
| run-510 | 2.06 | 2.92 | 100 % | 0.42 |
| run-511 | 1.59 | 2.09 | 100 % | 0.35 |
| run-512 | 2.80 | 4.07 | 100 % | 0.59 |
| run-513 | 1.19 | 2.27 | 100 % | 0.50 |
| run-514 | 1.58 | 2.94 | 100 % | 0.68 |
| run-515 | 1.99 | 3.18 | 100 % | 0.47 |
| run-516 | 1.46 | 2.87 | 100 % | 0.60 |
| **mean** | **1.79** | 2.83 | 100 % | 0.51 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam/poses/*.json --out runs/slam-5XXB-exam/shape.md`
