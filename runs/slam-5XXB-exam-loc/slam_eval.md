# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.6 | 0.22 | 1.1 / 2.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | nan | nan | 0 % | nan |
| run-510 | nan | nan | 0 % | nan |
| run-511 | nan | nan | 0 % | nan |
| run-512 | nan | nan | 0 % | nan |
| run-513 | nan | nan | 0 % | nan |
| run-514 | nan | nan | 0 % | nan |
| run-515 | nan | nan | 0 % | nan |
| run-516 | nan | nan | 0 % | nan |
| **mean** | **nan** | nan | 0 % | nan |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-loc/poses/*.json --out runs/slam-5XXB-exam-loc/shape.md`
