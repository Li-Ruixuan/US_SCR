# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.33 | 2.45 | 100 % | 0.52 |
| run-510 | 1.82 | 2.73 | 100 % | 0.39 |
| run-511 | 1.24 | 2.02 | 100 % | 0.32 |
| run-512 | 2.75 | 3.55 | 100 % | 0.48 |
| run-513 | 0.98 | 2.52 | 100 % | 0.41 |
| run-514 | 1.51 | 2.72 | 100 % | 0.66 |
| run-515 | 2.05 | 2.94 | 100 % | 0.46 |
| run-516 | 1.57 | 2.88 | 100 % | 0.58 |
| **mean** | **1.66** | 2.73 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-loc-r3/poses/*.json --out runs/paper_final/slam-5XXB-exam-loc-r3/shape.md`
