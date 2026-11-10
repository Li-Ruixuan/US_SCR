# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ60-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 7.1 | 1.6 | 0.21 | 1.1 / 2.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.68 | 3.95 | 100 % | 1.00 |
| run-510 | 2.65 | 23.88 | 100 % | 1.46 |
| run-511 | 1.48 | 5.96 | 100 % | 0.77 |
| run-512 | 12.87 | 166.00 | 100 % | 3.76 |
| run-513 | 1.45 | 4.69 | 100 % | 1.21 |
| run-514 | 1.59 | 3.80 | 100 % | 1.51 |
| run-515 | 2.69 | 30.63 | 100 % | 2.55 |
| run-516 | 2.17 | 83.11 | 100 % | 1.71 |
| **mean** | **3.32** | 40.25 | 100 % | 1.74 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ60-loc/poses/*.json --out runs/slam-5XXB-exam-occ60-loc/shape.md`
