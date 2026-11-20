# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.8 | 0.23 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 1.94 | 2.83 | 100 % | 0.51 |
| run-526 | 1.51 | 18.45 | 100 % | 0.92 |
| run-527 | 1.50 | 2.83 | 100 % | 0.79 |
| run-528 | 1.38 | 2.48 | 100 % | 0.76 |
| **mean** | **1.58** | 6.65 | 100 % | 0.74 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXD-exam-loc/poses/*.json --out runs/paper_final/slam-5XXD-exam-loc/shape.md`
