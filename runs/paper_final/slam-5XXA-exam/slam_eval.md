# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 9.3 | 4.0 | 0.40 | 1.7 / 5.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.65 | 4.18 | 100 % | 0.42 |
| run-502 | 2.83 | 4.30 | 100 % | 0.51 |
| run-503 | 2.95 | 3.76 | 100 % | 0.41 |
| run-504 | 3.61 | 5.12 | 100 % | 0.63 |
| run-505 | 3.42 | 4.61 | 100 % | 0.57 |
| run-506 | 3.25 | 3.96 | 100 % | 0.44 |
| run-507 | 4.34 | 5.33 | 100 % | 0.34 |
| run-508 | 3.30 | 4.31 | 100 % | 0.34 |
| **mean** | **3.29** | 4.45 | 100 % | 0.46 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-exam/poses/*.json --out runs/paper_final/slam-5XXA-exam/shape.md`
