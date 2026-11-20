# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-generic-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-501) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.9 | 2.7 | 0.30 | 2.4 / 6.2 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 3.09 | 4.54 | 100 % | 0.45 |
| run-502 | 3.44 | 4.95 | 100 % | 0.57 |
| run-503 | 3.43 | 4.38 | 100 % | 0.48 |
| run-504 | 3.08 | 4.61 | 100 % | 0.66 |
| run-505 | 2.57 | 4.17 | 100 % | 0.66 |
| run-506 | 2.50 | 3.70 | 100 % | 0.48 |
| run-507 | 2.70 | 3.38 | 100 % | 0.42 |
| run-508 | 2.19 | 3.28 | 100 % | 0.40 |
| **mean** | **2.88** | 4.13 | 100 % | 0.51 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-generic-loc/poses/*.json --out runs/paper_final/slam-5XXA-generic-loc/shape.md`
