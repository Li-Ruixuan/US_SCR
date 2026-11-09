# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.8 | 0.23 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 1.97 | 2.82 | 100 % | 0.56 |
| run-526 | 1.51 | 18.44 | 100 % | 0.99 |
| run-527 | 1.53 | 2.85 | 100 % | 0.80 |
| run-528 | 1.37 | 2.57 | 100 % | 0.80 |
| **mean** | **1.60** | 6.67 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXD-exam-loc/poses/*.json --out runs/slam-5XXD-exam-loc/shape.md`
