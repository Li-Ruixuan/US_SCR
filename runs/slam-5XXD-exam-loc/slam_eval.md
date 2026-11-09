# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.5 | 1.6 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 2.18 | 2.92 | 100 % | 0.58 |
| run-526 | 58.63 | 118.07 | 100 % | 2.69 |
| run-527 | nan | nan | 0 % | nan |
| run-528 | nan | nan | 0 % | nan |
| **mean** | **30.41** | 60.49 | 50 % | 1.63 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXD-exam-loc/poses/*.json --out runs/slam-5XXD-exam-loc/shape.md`
