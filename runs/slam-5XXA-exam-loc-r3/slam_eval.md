# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 9.1 | 3.6 | 0.37 | 1.5 / 4.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.57 | 4.79 | 100 % | 0.49 |
| run-502 | 2.89 | 4.84 | 100 % | 0.54 |
| run-503 | 3.08 | 4.60 | 100 % | 0.50 |
| run-504 | 4.15 | 5.97 | 100 % | 0.70 |
| run-505 | 3.90 | 4.98 | 100 % | 0.68 |
| run-506 | 3.60 | 4.60 | 100 % | 0.48 |
| run-507 | 5.13 | 6.07 | 100 % | 0.44 |
| run-508 | 3.65 | 5.01 | 100 % | 0.44 |
| **mean** | **3.62** | 5.11 | 100 % | 0.53 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam-loc-r3/poses/*.json --out runs/slam-5XXA-exam-loc-r3/shape.md`
