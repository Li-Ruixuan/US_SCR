# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-oldB-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-504) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.5 / 6.4 | 2.3 | 0.21 | 1.2 / 3.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 55.92 | 72.85 | 100 % | 0.72 |
| run-518 | 142.91 | 152.38 | 100 % | 0.71 |
| run-519 | 148.56 | 161.31 | 100 % | 1.01 |
| run-520 | 1139.34 | 1169.16 | 100 % | 1.67 |
| run-521 | 192.44 | 1150.02 | 100 % | 6.35 |
| run-522 | nan | nan | 0 % | nan |
| run-523 | nan | nan | 0 % | nan |
| run-524 | nan | nan | 0 % | nan |
| **mean** | **335.83** | 541.14 | 62 % | 2.09 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-oldB-loc/poses/*.json --out runs/slam-5XXC-oldB-loc/shape.md`
