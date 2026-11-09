# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.5 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.46 | 2.21 | 100 % | 0.34 |
| run-518 | 1.67 | 2.18 | 100 % | 0.29 |
| run-519 | 1.42 | 2.20 | 100 % | 0.38 |
| run-520 | 1.78 | 3.35 | 100 % | 0.58 |
| run-521 | 1.66 | 2.67 | 100 % | 0.40 |
| run-522 | 1.56 | 2.50 | 100 % | 0.37 |
| run-523 | 1.77 | 3.40 | 100 % | 0.67 |
| run-524 | 2.02 | 2.68 | 100 % | 0.45 |
| **mean** | **1.67** | 2.65 | 100 % | 0.44 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-online/poses/*.json --out runs/slam-5XXC-exam-online/shape.md`
