# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ30-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.2 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.88 | 2.41 | 100 % | 0.39 |
| run-518 | 1.76 | 2.46 | 100 % | 0.32 |
| run-519 | 2.10 | 2.67 | 100 % | 0.38 |
| run-520 | 1.76 | 3.40 | 100 % | 0.58 |
| run-521 | 2.55 | 3.29 | 100 % | 0.45 |
| run-522 | 2.26 | 3.50 | 100 % | 0.40 |
| run-523 | 2.50 | 3.89 | 100 % | 0.71 |
| run-524 | 2.15 | 3.28 | 100 % | 0.50 |
| **mean** | **2.12** | 3.11 | 100 % | 0.47 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ30-online/poses/*.json --out runs/slam-5XXC-exam-occ30-online/shape.md`
