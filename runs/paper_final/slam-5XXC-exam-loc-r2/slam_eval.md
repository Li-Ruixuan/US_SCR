# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.9 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.90 | 2.86 | 100 % | 0.31 |
| run-518 | 2.37 | 3.00 | 100 % | 0.25 |
| run-519 | 2.15 | 2.84 | 100 % | 0.33 |
| run-520 | 1.77 | 3.60 | 100 % | 0.49 |
| run-521 | 2.49 | 3.37 | 100 % | 0.37 |
| run-522 | 2.26 | 3.43 | 100 % | 0.35 |
| run-523 | 2.19 | 3.80 | 100 % | 0.65 |
| run-524 | 1.87 | 3.02 | 100 % | 0.40 |
| **mean** | **2.12** | 3.24 | 100 % | 0.40 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-loc-r2/poses/*.json --out runs/paper_final/slam-5XXC-exam-loc-r2/shape.md`
