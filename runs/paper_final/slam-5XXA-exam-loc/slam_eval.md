# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.0 / 9.2 | 3.9 | 0.38 | 1.6 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.51 | 5.34 | 100 % | 0.43 |
| run-502 | 2.94 | 4.78 | 100 % | 0.53 |
| run-503 | 3.16 | 4.97 | 100 % | 0.43 |
| run-504 | 4.47 | 6.59 | 100 % | 0.65 |
| run-505 | 3.94 | 5.08 | 100 % | 0.61 |
| run-506 | 3.73 | 4.99 | 100 % | 0.46 |
| run-507 | 5.81 | 6.72 | 100 % | 0.36 |
| run-508 | 3.80 | 5.24 | 100 % | 0.38 |
| **mean** | **3.79** | 5.46 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-exam-loc/poses/*.json --out runs/paper_final/slam-5XXA-exam-loc/shape.md`
