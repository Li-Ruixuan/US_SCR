# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ60-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.1 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.52 | 5.07 | 100 % | 0.52 |
| run-518 | 2.40 | 4.09 | 100 % | 0.41 |
| run-519 | 2.56 | 4.65 | 100 % | 0.53 |
| run-520 | 2.09 | 4.83 | 100 % | 0.71 |
| run-521 | 3.12 | 5.60 | 100 % | 0.52 |
| run-522 | 3.29 | 15.38 | 100 % | 0.55 |
| run-523 | 2.69 | 5.01 | 100 % | 0.76 |
| run-524 | 2.60 | 4.08 | 100 % | 0.52 |
| **mean** | **2.66** | 6.09 | 100 % | 0.57 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-occ60-online/poses/*.json --out runs/paper_final/slam-5XXC-exam-occ60-online/shape.md`
