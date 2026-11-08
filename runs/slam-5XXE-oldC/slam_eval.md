# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.6 | 0.25 | 1.2 / 3.6 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.26 | 2.99 | 100 % | 0.44 |
| run-530 | 3.41 | 4.04 | 100 % | 0.39 |
| run-531 | 3.94 | 4.91 | 100 % | 0.44 |
| run-532 | 2.62 | 3.38 | 100 % | 0.45 |
| **mean** | **3.06** | 3.83 | 100 % | 0.43 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-oldC/poses/*.json --out runs/slam-5XXE-oldC/shape.md`
