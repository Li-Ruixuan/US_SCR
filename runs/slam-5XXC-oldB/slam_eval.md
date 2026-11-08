# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-oldB/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-504) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.1 / 6.5 | 1.7 | 0.18 | 1.2 / 3.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 4.54 | 5.45 | 100 % | 0.40 |
| run-518 | 4.97 | 5.59 | 100 % | 0.27 |
| run-519 | 4.77 | 5.46 | 100 % | 0.35 |
| run-520 | 4.37 | 6.58 | 100 % | 0.61 |
| run-521 | 5.09 | 5.96 | 100 % | 0.40 |
| run-522 | 4.85 | 5.88 | 100 % | 0.34 |
| run-523 | 4.35 | 6.67 | 100 % | 0.69 |
| run-524 | 4.26 | 6.08 | 100 % | 0.46 |
| **mean** | **4.65** | 5.96 | 100 % | 0.44 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-oldB/poses/*.json --out runs/slam-5XXC-oldB/shape.md`
