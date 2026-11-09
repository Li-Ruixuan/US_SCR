# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.3 | 1.8 | 0.24 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 1.75 | 2.70 | 100 % | 0.58 |
| run-526 | 1.34 | 2.34 | 100 % | 0.66 |
| run-527 | 1.55 | 2.65 | 100 % | 0.81 |
| run-528 | 1.50 | 2.50 | 100 % | 0.80 |
| **mean** | **1.53** | 2.55 | 100 % | 0.71 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXD-exam-online/poses/*.json --out runs/slam-5XXD-exam-online/shape.md`
