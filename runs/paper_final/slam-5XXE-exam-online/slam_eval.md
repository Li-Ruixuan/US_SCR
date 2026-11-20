# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.6 | 1.3 | 0.24 | 0.8 / 1.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.46 | 2.09 | 100 % | 0.38 |
| run-530 | 2.47 | 3.15 | 100 % | 0.34 |
| run-531 | 3.35 | 4.80 | 100 % | 0.51 |
| run-532 | 1.69 | 2.35 | 100 % | 0.41 |
| **mean** | **2.24** | 3.10 | 100 % | 0.41 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-exam-online/poses/*.json --out runs/paper_final/slam-5XXE-exam-online/shape.md`
