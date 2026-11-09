# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.0 / 9.2 | 3.9 | 0.38 | 1.6 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.52 | 5.33 | 100 % | 0.49 |
| run-502 | 2.93 | 4.76 | 100 % | 0.55 |
| run-503 | 3.16 | 4.93 | 100 % | 0.48 |
| run-504 | 4.46 | 6.59 | 100 % | 0.70 |
| run-505 | 3.93 | 4.99 | 100 % | 0.70 |
| run-506 | 3.73 | 5.06 | 100 % | 0.51 |
| run-507 | 5.77 | 6.74 | 100 % | 0.44 |
| run-508 | 3.84 | 5.20 | 100 % | 0.47 |
| **mean** | **3.79** | 5.45 | 100 % | 0.54 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam-loc/poses/*.json --out runs/slam-5XXA-exam-loc/shape.md`
