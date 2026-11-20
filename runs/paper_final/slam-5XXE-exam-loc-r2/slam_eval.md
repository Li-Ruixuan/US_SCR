# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.5 | 1.5 | 0.24 | 0.8 / 1.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.48 | 2.45 | 100 % | 0.39 |
| run-530 | 3.20 | 4.11 | 100 % | 0.37 |
| run-531 | 3.89 | 5.20 | 100 % | 0.59 |
| run-532 | 2.65 | 3.69 | 100 % | 0.44 |
| **mean** | **2.81** | 3.86 | 100 % | 0.45 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-exam-loc-r2/poses/*.json --out runs/paper_final/slam-5XXE-exam-loc-r2/shape.md`
