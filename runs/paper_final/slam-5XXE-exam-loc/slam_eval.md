# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.5 | 1.3 | 0.24 | 0.8 / 1.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.33 | 2.33 | 100 % | 0.41 |
| run-530 | 2.98 | 4.61 | 100 % | 0.37 |
| run-531 | 3.80 | 6.33 | 100 % | 0.61 |
| run-532 | 2.45 | 3.77 | 100 % | 0.44 |
| **mean** | **2.64** | 4.26 | 100 % | 0.46 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-exam-loc/poses/*.json --out runs/paper_final/slam-5XXE-exam-loc/shape.md`
