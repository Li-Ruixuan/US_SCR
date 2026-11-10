# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ30-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 7.2 | 1.7 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.38 | 3.74 | 100 % | 0.56 |
| run-510 | 1.91 | 5.81 | 100 % | 0.61 |
| run-511 | 1.61 | 4.51 | 100 % | 0.52 |
| run-512 | 2.88 | 6.34 | 100 % | 0.95 |
| run-513 | 1.16 | 3.68 | 100 % | 0.55 |
| run-514 | 1.65 | 3.41 | 100 % | 0.74 |
| run-515 | 1.84 | 3.20 | 100 % | 0.57 |
| run-516 | 1.78 | 3.63 | 100 % | 0.72 |
| **mean** | **1.78** | 4.29 | 100 % | 0.65 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ30-reloc/poses/*.json --out runs/slam-5XXB-exam-occ30-reloc/shape.md`
