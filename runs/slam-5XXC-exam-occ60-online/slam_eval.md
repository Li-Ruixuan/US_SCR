# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ60-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.1 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.55 | 5.51 | 100 % | 0.57 |
| run-518 | 2.40 | 4.20 | 100 % | 0.45 |
| run-519 | 2.55 | 4.56 | 100 % | 0.61 |
| run-520 | 2.06 | 4.92 | 100 % | 0.87 |
| run-521 | 3.18 | 5.65 | 100 % | 0.57 |
| run-522 | 3.30 | 15.44 | 100 % | 0.60 |
| run-523 | 2.73 | 5.01 | 100 % | 0.82 |
| run-524 | 2.61 | 4.16 | 100 % | 0.61 |
| **mean** | **2.67** | 6.18 | 100 % | 0.64 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ60-online/poses/*.json --out runs/slam-5XXC-exam-occ60-online/shape.md`
