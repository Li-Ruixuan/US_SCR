# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ30-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 7.2 | 1.7 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.38 | 3.73 | 100 % | 0.58 |
| run-510 | 1.93 | 5.71 | 100 % | 0.57 |
| run-511 | 1.63 | 4.46 | 100 % | 0.47 |
| run-512 | 2.87 | 6.24 | 100 % | 0.81 |
| run-513 | 1.15 | 3.58 | 100 % | 0.52 |
| run-514 | 1.66 | 3.26 | 100 % | 0.74 |
| run-515 | 1.84 | 3.09 | 100 % | 0.56 |
| run-516 | 1.76 | 3.69 | 100 % | 0.68 |
| **mean** | **1.78** | 4.22 | 100 % | 0.61 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-occ30-reloc/poses/*.json --out runs/paper_final/slam-5XXB-exam-occ30-reloc/shape.md`
