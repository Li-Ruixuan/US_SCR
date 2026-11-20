# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ60-reloc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 7.2 | 1.6 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.46 | 2.93 | 100 % | 0.64 |
| run-510 | 1.80 | 4.89 | 100 % | 0.86 |
| run-511 | 1.49 | 3.55 | 100 % | 0.63 |
| run-512 | 2.92 | 6.38 | 100 % | 0.97 |
| run-513 | 1.51 | 3.48 | 100 % | 0.60 |
| run-514 | 1.64 | 3.45 | 100 % | 0.80 |
| run-515 | 1.98 | 3.16 | 100 % | 0.95 |
| run-516 | 1.85 | 4.53 | 100 % | 0.89 |
| **mean** | **1.83** | 4.05 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ60-reloc-r2/poses/*.json --out runs/slam-5XXB-exam-occ60-reloc-r2/shape.md`
