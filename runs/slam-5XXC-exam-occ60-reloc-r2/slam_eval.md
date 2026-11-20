# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ60-reloc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.4 | 1.6 | 0.23 | 1.2 / 3.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.59 | 4.04 | 100 % | 0.49 |
| run-518 | 1.67 | 3.37 | 100 % | 0.41 |
| run-519 | 1.51 | 3.33 | 100 % | 0.47 |
| run-520 | 1.88 | 3.78 | 100 % | 0.67 |
| run-521 | 1.84 | 3.06 | 100 % | 0.48 |
| run-522 | 1.69 | 4.96 | 100 % | 0.51 |
| run-523 | 2.20 | 4.19 | 100 % | 0.79 |
| run-524 | 2.11 | 4.21 | 100 % | 0.57 |
| **mean** | **1.81** | 3.87 | 100 % | 0.55 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ60-reloc-r2/poses/*.json --out runs/slam-5XXC-exam-occ60-reloc-r2/shape.md`
