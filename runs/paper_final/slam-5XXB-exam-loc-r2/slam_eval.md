# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.39 | 2.58 | 100 % | 0.52 |
| run-510 | 1.81 | 2.56 | 100 % | 0.40 |
| run-511 | 1.22 | 2.21 | 100 % | 0.33 |
| run-512 | 2.84 | 3.89 | 100 % | 0.50 |
| run-513 | 1.08 | 2.48 | 100 % | 0.41 |
| run-514 | 1.39 | 2.68 | 100 % | 0.65 |
| run-515 | 1.96 | 2.96 | 100 % | 0.46 |
| run-516 | 1.59 | 2.99 | 100 % | 0.59 |
| **mean** | **1.66** | 2.79 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-loc-r2/poses/*.json --out runs/paper_final/slam-5XXB-exam-loc-r2/shape.md`
