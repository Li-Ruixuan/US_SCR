# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.5 | 1.2 | 0.25 | 0.8 / 1.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.17 | 2.45 | 100 % | 0.44 |
| run-530 | 3.12 | 4.11 | 100 % | 0.50 |
| run-531 | 3.42 | 6.31 | 100 % | 0.63 |
| run-532 | 2.47 | 3.88 | 100 % | 0.49 |
| **mean** | **2.54** | 4.19 | 100 % | 0.51 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-exam-loc-r3/poses/*.json --out runs/slam-5XXE-exam-loc-r3/shape.md`
