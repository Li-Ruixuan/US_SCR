# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-oldB-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-504) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 2.0 | 0.21 | 1.2 / 3.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 46.07 | 55.97 | 100 % | 0.79 |
| run-518 | 51.32 | 56.51 | 100 % | 0.57 |
| run-519 | 46.81 | 55.21 | 100 % | 0.79 |
| run-520 | 48.50 | 57.16 | 100 % | 0.96 |
| run-521 | 55.27 | 59.52 | 100 % | 0.84 |
| run-522 | 48.00 | 56.64 | 100 % | 0.94 |
| run-523 | 50.32 | 57.16 | 100 % | 1.13 |
| run-524 | 3.26 | 4.70 | 100 % | 0.43 |
| **mean** | **43.69** | 50.36 | 100 % | 0.81 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-oldB-online/poses/*.json --out runs/slam-5XXC-oldB-online/shape.md`
