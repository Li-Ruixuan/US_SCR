# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.8 | 0.23 | 1.2 / 3.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 1.64 | 2.60 | 100 % | 0.57 |
| run-526 | 1.40 | 14.20 | 100 % | 0.97 |
| run-527 | 1.56 | 2.69 | 100 % | 0.82 |
| run-528 | 1.48 | 2.69 | 100 % | 0.81 |
| **mean** | **1.52** | 5.55 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXD-exam-loc-r2/poses/*.json --out runs/slam-5XXD-exam-loc-r2/shape.md`
