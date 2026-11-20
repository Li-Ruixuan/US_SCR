# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-oldB-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-504) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 2.2 | 0.22 | 1.3 / 3.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | nan | nan | 0 % | nan |
| run-518 | nan | nan | 0 % | nan |
| run-519 | nan | nan | 0 % | nan |
| run-520 | nan | nan | 0 % | nan |
| run-521 | 12.58 | 35.48 | 100 % | 0.97 |
| run-522 | 31.64 | 35.66 | 100 % | 0.43 |
| run-523 | 9.97 | 18.72 | 100 % | 0.95 |
| run-524 | 22.51 | 86.95 | 100 % | 1.17 |
| **mean** | **19.17** | 44.20 | 50 % | 0.88 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-oldB-loc/poses/*.json --out runs/paper_final/slam-5XXC-oldB-loc/shape.md`
