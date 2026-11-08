# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.5 | 1.8 | 0.23 | 0.8 / 2.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.23 | 3.10 | 100 % | 0.44 |
| run-530 | 2.76 | 3.41 | 100 % | 0.38 |
| run-531 | 2.70 | 4.15 | 100 % | 0.42 |
| run-532 | 2.56 | 3.60 | 100 % | 0.45 |
| **mean** | **2.56** | 3.57 | 100 % | 0.42 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-exam/poses/*.json --out runs/slam-5XXE-exam/shape.md`
