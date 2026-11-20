# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ60-loc-r4/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.3 | 1.6 | 0.23 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.30 | 6.00 | 100 % | 0.58 |
| run-518 | 2.39 | 4.88 | 100 % | 0.41 |
| run-519 | 2.52 | 41.69 | 100 % | 1.16 |
| run-520 | 2.31 | 7.48 | 100 % | 1.00 |
| run-521 | 2.74 | 7.19 | 100 % | 0.65 |
| run-522 | 2.29 | 5.52 | 100 % | 0.56 |
| run-523 | 2.32 | 5.62 | 100 % | 0.94 |
| run-524 | 2.30 | 5.52 | 100 % | 0.74 |
| **mean** | **2.40** | 10.49 | 100 % | 0.76 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ60-loc-r4/poses/*.json --out runs/slam-5XXC-exam-occ60-loc-r4/shape.md`
