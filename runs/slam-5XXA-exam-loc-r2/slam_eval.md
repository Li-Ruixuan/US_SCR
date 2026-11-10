# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 9.0 | 3.6 | 0.37 | 1.6 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.42 | 4.66 | 100 % | 0.47 |
| run-502 | 2.70 | 4.54 | 100 % | 0.53 |
| run-503 | 2.72 | 4.36 | 100 % | 0.46 |
| run-504 | 4.10 | 6.07 | 100 % | 0.70 |
| run-505 | 3.58 | 4.65 | 100 % | 0.67 |
| run-506 | 3.25 | 4.63 | 100 % | 0.50 |
| run-507 | 5.23 | 6.21 | 100 % | 0.46 |
| run-508 | 3.41 | 4.84 | 100 % | 0.43 |
| **mean** | **3.43** | 5.00 | 100 % | 0.53 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam-loc-r2/poses/*.json --out runs/slam-5XXA-exam-loc-r2/shape.md`
