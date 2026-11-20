# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.3 | 1.8 | 0.24 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 1.75 | 2.65 | 100 % | 0.52 |
| run-526 | 1.33 | 2.28 | 100 % | 0.59 |
| run-527 | 1.55 | 2.56 | 100 % | 0.79 |
| run-528 | 1.47 | 2.43 | 100 % | 0.75 |
| **mean** | **1.52** | 2.48 | 100 % | 0.66 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXD-exam-online/poses/*.json --out runs/paper_final/slam-5XXD-exam-online/shape.md`
