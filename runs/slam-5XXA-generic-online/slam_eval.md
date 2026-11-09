# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-generic-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-501) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.9 | 3.1 | 0.31 | 2.4 / 6.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 3.30 | 4.15 | 100 % | 0.43 |
| run-502 | 3.44 | 4.89 | 100 % | 0.51 |
| run-503 | 3.41 | 4.13 | 100 % | 0.42 |
| run-504 | 3.18 | 5.02 | 100 % | 0.66 |
| run-505 | 2.90 | 4.36 | 100 % | 0.63 |
| run-506 | 3.06 | 4.16 | 100 % | 0.45 |
| run-507 | 3.02 | 3.72 | 100 % | 0.39 |
| run-508 | 3.01 | 3.80 | 100 % | 0.40 |
| **mean** | **3.16** | 4.28 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-generic-online/poses/*.json --out runs/slam-5XXA-generic-online/shape.md`
