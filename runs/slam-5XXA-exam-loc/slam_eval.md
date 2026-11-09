# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-loc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.0 / 9.1 | 3.9 | 0.39 | 1.5 / 4.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.23 | 4.72 | 100 % | 0.50 |
| run-502 | 77.96 | 117.31 | 100 % | 2.16 |
| run-503 | nan | nan | 0 % | nan |
| run-504 | nan | nan | 0 % | nan |
| run-505 | nan | nan | 0 % | nan |
| run-506 | nan | nan | 0 % | nan |
| run-507 | nan | nan | 0 % | nan |
| run-508 | nan | nan | 0 % | nan |
| **mean** | **40.10** | 61.01 | 25 % | 1.33 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam-loc/poses/*.json --out runs/slam-5XXA-exam-loc/shape.md`
