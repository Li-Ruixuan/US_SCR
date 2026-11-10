# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ30-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.46 | 3.56 | 100 % | 0.61 |
| run-510 | 1.72 | 4.40 | 100 % | 0.59 |
| run-511 | 1.57 | 2.92 | 100 % | 0.44 |
| run-512 | 132.20 | 139.10 | 100 % | 1.55 |
| run-513 | 1.32 | 3.35 | 100 % | 0.56 |
| run-514 | 1.45 | 3.06 | 100 % | 0.75 |
| run-515 | 1.82 | 3.12 | 100 % | 0.67 |
| run-516 | 1.76 | 3.14 | 100 % | 0.76 |
| **mean** | **17.91** | 20.33 | 100 % | 0.74 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ30-loc/poses/*.json --out runs/slam-5XXB-exam-occ30-loc/shape.md`
