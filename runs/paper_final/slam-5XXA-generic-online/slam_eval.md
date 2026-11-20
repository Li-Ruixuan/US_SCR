# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-generic-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-501) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.9 | 3.1 | 0.31 | 2.4 / 6.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 3.29 | 4.14 | 100 % | 0.40 |
| run-502 | 3.42 | 4.88 | 100 % | 0.50 |
| run-503 | 3.40 | 4.15 | 100 % | 0.40 |
| run-504 | 3.19 | 4.96 | 100 % | 0.62 |
| run-505 | 2.89 | 4.38 | 100 % | 0.57 |
| run-506 | 3.05 | 4.14 | 100 % | 0.44 |
| run-507 | 3.02 | 3.69 | 100 % | 0.33 |
| run-508 | 3.00 | 3.81 | 100 % | 0.36 |
| **mean** | **3.16** | 4.27 | 100 % | 0.45 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-generic-online/poses/*.json --out runs/paper_final/slam-5XXA-generic-online/shape.md`
