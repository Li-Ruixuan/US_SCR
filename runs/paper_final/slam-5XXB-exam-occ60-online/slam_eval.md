# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ60-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.2 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.42 | 3.26 | 100 % | 0.67 |
| run-510 | 2.04 | 5.80 | 100 % | 0.81 |
| run-511 | 1.50 | 4.31 | 100 % | 0.66 |
| run-512 | 5.79 | 51.52 | 100 % | 1.62 |
| run-513 | 1.49 | 3.90 | 100 % | 0.58 |
| run-514 | 1.46 | 3.38 | 100 % | 0.81 |
| run-515 | 38.65 | 48.40 | 100 % | 1.19 |
| run-516 | 2.74 | 46.80 | 100 % | 1.21 |
| **mean** | **6.89** | 20.92 | 100 % | 0.94 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-occ60-online/poses/*.json --out runs/paper_final/slam-5XXB-exam-occ60-online/shape.md`
