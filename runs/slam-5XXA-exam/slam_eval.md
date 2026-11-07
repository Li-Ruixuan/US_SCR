# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam/CameraTrajectory.txt`)

One alignment of the session and the camera calibration (fixed from `runs/repro/map-3XX/map.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.5 / 11.7 | 15.5 | 0.95 | 2.1 / 7.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 16.94 | 18.30 | 100 % | 0.54 |
| run-502 | 16.53 | 18.16 | 100 % | 0.60 |
| run-503 | 16.86 | 17.74 | 100 % | 0.49 |
| run-504 | 16.32 | 18.62 | 100 % | 1.11 |
| run-505 | 16.61 | 17.81 | 100 % | 0.78 |
| run-506 | 16.61 | 17.20 | 100 % | 0.49 |
| run-507 | 17.41 | 18.17 | 100 % | 0.40 |
| run-508 | 16.36 | 17.01 | 100 % | 0.38 |
| **mean** | **16.70** | 17.88 | 100 % | 0.60 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam/poses/*.json --out runs/slam-5XXA-exam/shape.md`
