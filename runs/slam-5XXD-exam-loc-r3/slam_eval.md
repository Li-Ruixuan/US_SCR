# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.7 | 0.23 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 2.12 | 3.01 | 100 % | 0.56 |
| run-526 | 1.51 | 4.95 | 100 % | 0.98 |
| run-527 | 1.68 | 2.99 | 100 % | 0.83 |
| run-528 | 1.56 | 2.62 | 100 % | 0.81 |
| **mean** | **1.71** | 3.39 | 100 % | 0.80 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXD-exam-loc-r3/poses/*.json --out runs/slam-5XXD-exam-loc-r3/shape.md`
