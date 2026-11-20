# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.5 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.44 | 2.23 | 100 % | 0.31 |
| run-518 | 1.66 | 2.16 | 100 % | 0.25 |
| run-519 | 1.42 | 2.15 | 100 % | 0.33 |
| run-520 | 1.73 | 3.32 | 100 % | 0.49 |
| run-521 | 1.65 | 2.66 | 100 % | 0.37 |
| run-522 | 1.56 | 2.50 | 100 % | 0.34 |
| run-523 | 1.77 | 3.43 | 100 % | 0.62 |
| run-524 | 2.02 | 2.65 | 100 % | 0.40 |
| **mean** | **1.66** | 2.64 | 100 % | 0.39 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-online/poses/*.json --out runs/paper_final/slam-5XXC-exam-online/shape.md`
