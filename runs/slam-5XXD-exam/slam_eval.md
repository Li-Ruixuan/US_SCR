# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.6 | 2.1 | 0.23 | 1.3 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 2.36 | 3.23 | 100 % | 0.58 |
| run-526 | 1.92 | 2.91 | 100 % | 0.70 |
| run-527 | 2.09 | 3.01 | 100 % | 0.85 |
| run-528 | 2.08 | 3.05 | 100 % | 0.80 |
| **mean** | **2.11** | 3.05 | 100 % | 0.73 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXD-exam/poses/*.json --out runs/slam-5XXD-exam/shape.md`
