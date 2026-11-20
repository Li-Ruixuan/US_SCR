# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ30-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 2.2 | 0.24 | 1.2 / 3.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.86 | 2.40 | 100 % | 0.36 |
| run-518 | 1.77 | 2.44 | 100 % | 0.29 |
| run-519 | 2.11 | 2.66 | 100 % | 0.35 |
| run-520 | 1.72 | 3.33 | 100 % | 0.49 |
| run-521 | 2.57 | 3.28 | 100 % | 0.41 |
| run-522 | 2.26 | 3.48 | 100 % | 0.38 |
| run-523 | 2.49 | 3.90 | 100 % | 0.65 |
| run-524 | 2.11 | 3.27 | 100 % | 0.45 |
| **mean** | **2.11** | 3.10 | 100 % | 0.42 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-occ30-online/poses/*.json --out runs/paper_final/slam-5XXC-exam-occ30-online/shape.md`
