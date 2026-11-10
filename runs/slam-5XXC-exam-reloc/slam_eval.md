# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.5 | 1.7 | 0.23 | 1.2 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 2.17 | 2.85 | 100 % | 0.34 |
| run-518 | 2.38 | 2.98 | 100 % | 0.30 |
| run-519 | 2.07 | 3.00 | 100 % | 0.38 |
| run-520 | 1.98 | 3.62 | 100 % | 0.60 |
| run-521 | 2.65 | 3.52 | 100 % | 0.42 |
| run-522 | 2.57 | 3.61 | 100 % | 0.36 |
| run-523 | 2.26 | 3.96 | 100 % | 0.71 |
| run-524 | 2.07 | 3.25 | 100 % | 0.45 |
| **mean** | **2.27** | 3.35 | 100 % | 0.44 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-reloc/poses/*.json --out runs/slam-5XXC-exam-reloc/shape.md`
