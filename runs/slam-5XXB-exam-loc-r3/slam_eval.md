# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.34 | 2.51 | 100 % | 0.49 |
| run-510 | 1.82 | 2.74 | 100 % | 0.42 |
| run-511 | 1.23 | 2.03 | 100 % | 0.33 |
| run-512 | 2.75 | 3.60 | 100 % | 0.55 |
| run-513 | 0.99 | 2.57 | 100 % | 0.43 |
| run-514 | 1.48 | 2.71 | 100 % | 0.64 |
| run-515 | 2.05 | 2.98 | 100 % | 0.46 |
| run-516 | 1.57 | 2.92 | 100 % | 0.60 |
| **mean** | **1.65** | 2.76 | 100 % | 0.49 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-loc-r3/poses/*.json --out runs/slam-5XXB-exam-loc-r3/shape.md`
