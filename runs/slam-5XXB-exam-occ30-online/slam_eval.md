# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ30-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.41 | 3.53 | 100 % | 0.55 |
| run-510 | 1.64 | 3.99 | 100 % | 0.53 |
| run-511 | 1.60 | 2.84 | 100 % | 0.41 |
| run-512 | 2.90 | 6.65 | 100 % | 0.71 |
| run-513 | 1.40 | 3.42 | 100 % | 0.50 |
| run-514 | 1.55 | 3.17 | 100 % | 0.73 |
| run-515 | 1.77 | 2.97 | 100 % | 0.54 |
| run-516 | 1.78 | 2.93 | 100 % | 0.66 |
| **mean** | **1.76** | 3.69 | 100 % | 0.58 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ30-online/poses/*.json --out runs/slam-5XXB-exam-occ30-online/shape.md`
