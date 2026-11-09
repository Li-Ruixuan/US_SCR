# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-generic-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-501) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.9 | 2.7 | 0.30 | 2.4 / 6.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 3.12 | 4.55 | 100 % | 0.53 |
| run-502 | 3.45 | 4.89 | 100 % | 0.61 |
| run-503 | 3.42 | 4.36 | 100 % | 0.57 |
| run-504 | 3.10 | 4.65 | 100 % | 0.72 |
| run-505 | 2.59 | 4.23 | 100 % | 0.78 |
| run-506 | 2.50 | 3.71 | 100 % | 0.55 |
| run-507 | 2.69 | 3.41 | 100 % | 0.54 |
| run-508 | 2.20 | 3.26 | 100 % | 0.49 |
| **mean** | **2.88** | 4.13 | 100 % | 0.60 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-generic-loc/poses/*.json --out runs/slam-5XXA-generic-loc/shape.md`
