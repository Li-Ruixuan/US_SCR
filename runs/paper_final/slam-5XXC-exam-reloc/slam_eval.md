# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.15 | 2.85 | 100 % | 0.31 |
| run-518 | 2.39 | 2.96 | 100 % | 0.25 |
| run-519 | 2.08 | 2.99 | 100 % | 0.33 |
| run-520 | 1.96 | 3.65 | 100 % | 0.50 |
| run-521 | 2.66 | 3.50 | 100 % | 0.37 |
| run-522 | 2.56 | 3.60 | 100 % | 0.34 |
| run-523 | 2.26 | 3.94 | 100 % | 0.64 |
| run-524 | 2.08 | 3.23 | 100 % | 0.39 |
| **mean** | **2.27** | 3.34 | 100 % | 0.39 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-reloc/poses/*.json --out runs/paper_final/slam-5XXC-exam-reloc/shape.md`
