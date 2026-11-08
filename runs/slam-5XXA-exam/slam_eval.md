# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 9.3 | 4.0 | 0.40 | 1.7 / 5.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.65 | 4.18 | 100 % | 0.46 |
| run-502 | 2.83 | 4.25 | 100 % | 0.52 |
| run-503 | 2.94 | 3.78 | 100 % | 0.45 |
| run-504 | 3.64 | 5.15 | 100 % | 0.78 |
| run-505 | 3.41 | 4.43 | 100 % | 0.62 |
| run-506 | 3.23 | 3.96 | 100 % | 0.45 |
| run-507 | 4.33 | 5.37 | 100 % | 0.38 |
| run-508 | 3.29 | 4.28 | 100 % | 0.36 |
| **mean** | **3.29** | 4.42 | 100 % | 0.50 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam/poses/*.json --out runs/slam-5XXA-exam/shape.md`
