# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.5 | 1.8 | 0.23 | 0.8 / 2.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 2.24 | 3.12 | 100 % | 0.40 |
| run-530 | 2.77 | 3.35 | 100 % | 0.34 |
| run-531 | 2.71 | 4.15 | 100 % | 0.49 |
| run-532 | 2.58 | 3.59 | 100 % | 0.41 |
| **mean** | **2.57** | 3.55 | 100 % | 0.41 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-exam/poses/*.json --out runs/paper_final/slam-5XXE-exam/shape.md`
