# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ30-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 1.9 | 0.24 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.83 | 2.47 | 100 % | 0.46 |
| run-518 | 1.96 | 2.78 | 100 % | 0.38 |
| run-519 | 1.94 | 2.83 | 100 % | 0.48 |
| run-520 | 1.83 | 3.47 | 100 % | 0.67 |
| run-521 | 2.25 | 3.28 | 100 % | 0.50 |
| run-522 | 2.05 | 3.39 | 100 % | 0.44 |
| run-523 | 2.26 | 3.92 | 100 % | 0.85 |
| run-524 | 1.98 | 3.48 | 100 % | 0.55 |
| **mean** | **2.01** | 3.20 | 100 % | 0.54 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ30-reloc/poses/*.json --out runs/slam-5XXC-exam-occ30-reloc/shape.md`
