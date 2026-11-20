# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ30-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.45 | 3.57 | 100 % | 0.60 |
| run-510 | 1.73 | 4.40 | 100 % | 0.54 |
| run-511 | 1.58 | 2.97 | 100 % | 0.42 |
| run-512 | 131.92 | 139.11 | 100 % | 1.47 |
| run-513 | 1.33 | 3.32 | 100 % | 0.52 |
| run-514 | 1.50 | 2.98 | 100 % | 0.73 |
| run-515 | 1.79 | 3.08 | 100 % | 0.63 |
| run-516 | 1.77 | 3.03 | 100 % | 0.66 |
| **mean** | **17.88** | 20.31 | 100 % | 0.70 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-occ30-loc/poses/*.json --out runs/paper_final/slam-5XXB-exam-occ30-loc/shape.md`
