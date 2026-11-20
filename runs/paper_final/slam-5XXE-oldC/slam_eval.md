# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.6 | 0.25 | 1.2 / 3.6 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.23 | 3.06 | 100 % | 0.40 |
| run-530 | 3.42 | 4.02 | 100 % | 0.34 |
| run-531 | 3.94 | 4.90 | 100 % | 0.51 |
| run-532 | 2.62 | 3.36 | 100 % | 0.42 |
| **mean** | **3.05** | 3.83 | 100 % | 0.42 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-oldC/poses/*.json --out runs/paper_final/slam-5XXE-oldC/shape.md`
