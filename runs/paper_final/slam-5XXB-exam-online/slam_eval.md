# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.6 | 0.22 | 1.2 / 2.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.10 | 2.39 | 100 % | 0.51 |
| run-510 | 1.76 | 2.85 | 100 % | 0.37 |
| run-511 | 1.55 | 2.08 | 100 % | 0.31 |
| run-512 | 3.00 | 4.23 | 100 % | 0.45 |
| run-513 | 1.34 | 2.65 | 100 % | 0.41 |
| run-514 | 1.62 | 2.78 | 100 % | 0.66 |
| run-515 | 2.05 | 3.16 | 100 % | 0.46 |
| run-516 | 1.88 | 3.14 | 100 % | 0.58 |
| **mean** | **1.79** | 2.91 | 100 % | 0.47 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-online/poses/*.json --out runs/paper_final/slam-5XXB-exam-online/shape.md`
