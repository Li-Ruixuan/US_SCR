# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-oldB/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-504) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.1 / 6.5 | 1.7 | 0.18 | 1.2 / 3.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 4.55 | 5.45 | 100 % | 0.39 |
| run-518 | 4.95 | 5.57 | 100 % | 0.24 |
| run-519 | 4.82 | 5.44 | 100 % | 0.32 |
| run-520 | 4.39 | 6.49 | 100 % | 0.53 |
| run-521 | 5.07 | 5.98 | 100 % | 0.37 |
| run-522 | 4.84 | 5.92 | 100 % | 0.34 |
| run-523 | 4.30 | 6.77 | 100 % | 0.63 |
| run-524 | 4.28 | 6.09 | 100 % | 0.40 |
| **mean** | **4.65** | 5.96 | 100 % | 0.40 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-oldB/poses/*.json --out runs/paper_final/slam-5XXC-oldB/shape.md`
