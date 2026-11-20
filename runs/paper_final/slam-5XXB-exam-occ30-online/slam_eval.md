# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ30-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.40 | 3.49 | 100 % | 0.55 |
| run-510 | 1.66 | 3.83 | 100 % | 0.49 |
| run-511 | 1.62 | 2.82 | 100 % | 0.39 |
| run-512 | 2.87 | 6.77 | 100 % | 0.63 |
| run-513 | 1.38 | 3.37 | 100 % | 0.48 |
| run-514 | 1.58 | 3.00 | 100 % | 0.72 |
| run-515 | 1.77 | 2.93 | 100 % | 0.53 |
| run-516 | 1.82 | 2.87 | 100 % | 0.63 |
| **mean** | **1.76** | 3.63 | 100 % | 0.55 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-occ30-online/poses/*.json --out runs/paper_final/slam-5XXB-exam-occ30-online/shape.md`
