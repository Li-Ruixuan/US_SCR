# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ60-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 7.1 | 1.6 | 0.21 | 1.1 / 2.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.62 | 3.99 | 100 % | 0.89 |
| run-510 | 2.65 | 23.77 | 100 % | 1.33 |
| run-511 | 1.52 | 5.60 | 100 % | 0.68 |
| run-512 | 13.02 | 165.99 | 100 % | 3.62 |
| run-513 | 1.45 | 4.48 | 100 % | 1.15 |
| run-514 | 1.62 | 4.18 | 100 % | 1.38 |
| run-515 | 2.70 | 30.69 | 100 % | 2.45 |
| run-516 | 2.11 | 83.07 | 100 % | 1.53 |
| **mean** | **3.34** | 40.22 | 100 % | 1.63 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-occ60-loc/poses/*.json --out runs/paper_final/slam-5XXB-exam-occ60-loc/shape.md`
