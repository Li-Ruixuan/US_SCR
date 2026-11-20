# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ60-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.3 | 0.25 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 3.38 | 6.53 | 100 % | 0.60 |
| run-518 | 3.41 | 6.42 | 100 % | 0.43 |
| run-519 | 3.59 | 64.25 | 100 % | 1.22 |
| run-520 | nan | nan | 0 % | nan |
| run-521 | nan | nan | 0 % | nan |
| run-522 | nan | nan | 0 % | nan |
| run-523 | nan | nan | 0 % | nan |
| run-524 | nan | nan | 0 % | nan |
| **mean** | **3.46** | 25.74 | 38 % | 0.75 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-occ60-loc/poses/*.json --out runs/paper_final/slam-5XXC-exam-occ60-loc/shape.md`
