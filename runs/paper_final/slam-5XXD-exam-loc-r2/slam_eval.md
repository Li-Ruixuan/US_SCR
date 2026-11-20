# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.8 | 0.23 | 1.2 / 3.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 1.64 | 2.58 | 100 % | 0.52 |
| run-526 | 1.42 | 14.78 | 100 % | 0.91 |
| run-527 | 1.57 | 2.65 | 100 % | 0.79 |
| run-528 | 1.46 | 2.53 | 100 % | 0.77 |
| **mean** | **1.52** | 5.63 | 100 % | 0.75 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXD-exam-loc-r2/poses/*.json --out runs/paper_final/slam-5XXD-exam-loc-r2/shape.md`
