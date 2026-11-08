# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.04 | 2.55 | 100 % | 0.34 |
| run-518 | 2.12 | 2.66 | 100 % | 0.30 |
| run-519 | 1.95 | 2.71 | 100 % | 0.39 |
| run-520 | 1.69 | 3.41 | 100 % | 0.56 |
| run-521 | 2.20 | 3.05 | 100 % | 0.41 |
| run-522 | 0.82 | 2.19 | 100 % | 0.47 |
| run-523 | 2.37 | 4.71 | 100 % | 1.19 |
| run-524 | 1.80 | 2.68 | 100 % | 0.46 |
| **mean** | **1.88** | 3.00 | 100 % | 0.51 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam/poses/*.json --out runs/slam-5XXC-exam/shape.md`
