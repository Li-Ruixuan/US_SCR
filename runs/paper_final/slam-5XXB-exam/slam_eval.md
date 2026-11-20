# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.9 | 0.23 | 1.2 / 3.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.67 | 2.35 | 100 % | 0.52 |
| run-510 | 2.05 | 2.92 | 100 % | 0.39 |
| run-511 | 1.59 | 2.10 | 100 % | 0.33 |
| run-512 | 2.80 | 4.08 | 100 % | 0.49 |
| run-513 | 1.17 | 2.25 | 100 % | 0.44 |
| run-514 | 1.60 | 2.92 | 100 % | 0.67 |
| run-515 | 2.01 | 3.14 | 100 % | 0.47 |
| run-516 | 1.46 | 2.85 | 100 % | 0.58 |
| **mean** | **1.79** | 2.83 | 100 % | 0.49 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam/poses/*.json --out runs/paper_final/slam-5XXB-exam/shape.md`
