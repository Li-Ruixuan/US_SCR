# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.6 | 0.23 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | nan | nan | 0 % | nan |
| run-530 | nan | nan | 0 % | nan |
| run-531 | nan | nan | 0 % | nan |
| run-532 | nan | nan | 0 % | nan |
| **mean** | **nan** | nan | 0 % | nan |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-oldC-loc/poses/*.json --out runs/slam-5XXE-oldC-loc/shape.md`
