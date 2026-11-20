# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 9.0 | 3.6 | 0.37 | 1.6 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.40 | 4.65 | 100 % | 0.42 |
| run-502 | 2.68 | 4.61 | 100 % | 0.52 |
| run-503 | 2.73 | 4.34 | 100 % | 0.41 |
| run-504 | 4.08 | 6.05 | 100 % | 0.65 |
| run-505 | 3.60 | 4.78 | 100 % | 0.60 |
| run-506 | 3.27 | 4.55 | 100 % | 0.46 |
| run-507 | 5.24 | 6.20 | 100 % | 0.37 |
| run-508 | 3.42 | 4.85 | 100 % | 0.36 |
| **mean** | **3.43** | 5.00 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-exam-loc-r2/poses/*.json --out runs/paper_final/slam-5XXA-exam-loc-r2/shape.md`
