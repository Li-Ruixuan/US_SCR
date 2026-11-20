# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-oldB-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-504) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 2.0 | 0.21 | 1.2 / 3.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 46.08 | 56.00 | 100 % | 0.79 |
| run-518 | 51.31 | 56.52 | 100 % | 0.56 |
| run-519 | 46.83 | 55.11 | 100 % | 0.77 |
| run-520 | 48.53 | 57.16 | 100 % | 0.91 |
| run-521 | 55.25 | 59.48 | 100 % | 0.83 |
| run-522 | 48.02 | 56.56 | 100 % | 0.94 |
| run-523 | 50.33 | 57.22 | 100 % | 1.08 |
| run-524 | 3.27 | 4.73 | 100 % | 0.39 |
| **mean** | **43.70** | 50.35 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-oldB-online/poses/*.json --out runs/paper_final/slam-5XXC-oldB-online/shape.md`
