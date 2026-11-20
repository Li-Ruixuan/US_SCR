# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.04 | 2.58 | 100 % | 0.31 |
| run-518 | 2.13 | 2.65 | 100 % | 0.25 |
| run-519 | 1.96 | 2.71 | 100 % | 0.33 |
| run-520 | 1.72 | 3.39 | 100 % | 0.48 |
| run-521 | 2.19 | 3.07 | 100 % | 0.38 |
| run-522 | 0.82 | 2.18 | 100 % | 0.39 |
| run-523 | 2.40 | 4.87 | 100 % | 0.95 |
| run-524 | 1.80 | 2.64 | 100 % | 0.40 |
| **mean** | **1.88** | 3.01 | 100 % | 0.44 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam/poses/*.json --out runs/paper_final/slam-5XXC-exam/shape.md`
