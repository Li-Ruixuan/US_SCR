# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.9 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 51.07 | 106.13 | 100 % | 3.18 |
| run-518 | nan | nan | 0 % | nan |
| run-519 | nan | nan | 0 % | nan |
| run-520 | nan | nan | 0 % | nan |
| run-521 | nan | nan | 0 % | nan |
| run-522 | nan | nan | 0 % | nan |
| run-523 | nan | nan | 0 % | nan |
| run-524 | nan | nan | 0 % | nan |
| **mean** | **51.07** | 106.13 | 12 % | 3.18 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-loc/poses/*.json --out runs/slam-5XXC-exam-loc/shape.md`
