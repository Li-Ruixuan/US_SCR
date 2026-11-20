# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-loc-r3/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 9.1 | 3.6 | 0.37 | 1.5 / 4.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.59 | 4.79 | 100 % | 0.42 |
| run-502 | 2.90 | 4.85 | 100 % | 0.52 |
| run-503 | 3.12 | 4.62 | 100 % | 0.42 |
| run-504 | 4.14 | 5.94 | 100 % | 0.65 |
| run-505 | 3.89 | 5.15 | 100 % | 0.60 |
| run-506 | 3.63 | 4.60 | 100 % | 0.44 |
| run-507 | 5.11 | 6.08 | 100 % | 0.35 |
| run-508 | 3.64 | 5.09 | 100 % | 0.37 |
| **mean** | **3.63** | 5.14 | 100 % | 0.47 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-exam-loc-r3/poses/*.json --out runs/paper_final/slam-5XXA-exam-loc-r3/shape.md`
