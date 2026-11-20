# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.6 | 2.1 | 0.23 | 1.3 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 2.36 | 3.21 | 100 % | 0.51 |
| run-526 | 1.90 | 2.92 | 100 % | 0.62 |
| run-527 | 2.07 | 2.95 | 100 % | 0.81 |
| run-528 | 2.09 | 2.98 | 100 % | 0.76 |
| **mean** | **2.10** | 3.01 | 100 % | 0.67 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXD-exam/poses/*.json --out runs/paper_final/slam-5XXD-exam/shape.md`
