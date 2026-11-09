# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.0 / 9.1 | 3.7 | 0.37 | 1.6 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.09 | 4.48 | 100 % | 0.44 |
| run-502 | 2.82 | 4.77 | 100 % | 0.50 |
| run-503 | 2.99 | 4.22 | 100 % | 0.41 |
| run-504 | 4.25 | 5.89 | 100 % | 0.65 |
| run-505 | 3.95 | 4.99 | 100 % | 0.60 |
| run-506 | 3.63 | 4.60 | 100 % | 0.45 |
| run-507 | 4.87 | 5.90 | 100 % | 0.40 |
| run-508 | 3.58 | 4.64 | 100 % | 0.39 |
| **mean** | **3.52** | 4.94 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam-online/poses/*.json --out runs/slam-5XXA-exam-online/shape.md`
