# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.0 / 9.1 | 3.7 | 0.37 | 1.6 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.09 | 4.49 | 100 % | 0.41 |
| run-502 | 2.80 | 4.86 | 100 % | 0.51 |
| run-503 | 3.02 | 4.18 | 100 % | 0.39 |
| run-504 | 4.28 | 5.91 | 100 % | 0.63 |
| run-505 | 3.96 | 5.01 | 100 % | 0.56 |
| run-506 | 3.64 | 4.58 | 100 % | 0.44 |
| run-507 | 4.85 | 5.88 | 100 % | 0.33 |
| run-508 | 3.59 | 4.60 | 100 % | 0.36 |
| **mean** | **3.53** | 4.94 | 100 % | 0.45 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-exam-online/poses/*.json --out runs/paper_final/slam-5XXA-exam-online/shape.md`
