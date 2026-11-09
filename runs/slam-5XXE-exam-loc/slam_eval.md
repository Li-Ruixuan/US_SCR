# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.0 / 5.6 | 1.6 | 0.24 | 0.8 / 1.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.55 | 2.23 | 100 % | 0.43 |
| run-530 | nan | nan | 0 % | nan |
| run-531 | nan | nan | 0 % | nan |
| run-532 | nan | nan | 0 % | nan |
| **mean** | **1.55** | 2.23 | 25 % | 0.43 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-exam-loc/poses/*.json --out runs/slam-5XXE-exam-loc/shape.md`
