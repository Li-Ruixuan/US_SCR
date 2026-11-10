# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ60-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.43 | 3.29 | 100 % | 0.71 |
| run-510 | 2.01 | 6.45 | 100 % | 0.92 |
| run-511 | 1.48 | 5.06 | 100 % | 0.75 |
| run-512 | 5.91 | 51.64 | 100 % | 1.79 |
| run-513 | 1.45 | 3.98 | 100 % | 0.64 |
| run-514 | 1.46 | 3.61 | 100 % | 0.87 |
| run-515 | 38.56 | 48.40 | 100 % | 1.31 |
| run-516 | 2.76 | 46.66 | 100 % | 1.36 |
| **mean** | **6.88** | 21.14 | 100 % | 1.04 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ60-online/poses/*.json --out runs/slam-5XXB-exam-occ60-online/shape.md`
