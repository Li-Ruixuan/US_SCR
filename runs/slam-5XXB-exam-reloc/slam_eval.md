# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.7 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.51 | 2.53 | 100 % | 0.50 |
| run-510 | 1.73 | 2.57 | 100 % | 0.41 |
| run-511 | 1.21 | 1.92 | 100 % | 0.32 |
| run-512 | 2.72 | 4.41 | 100 % | 0.57 |
| run-513 | 1.04 | 2.39 | 100 % | 0.43 |
| run-514 | 1.43 | 2.62 | 100 % | 0.65 |
| run-515 | 1.90 | 2.81 | 100 % | 0.45 |
| run-516 | 1.47 | 2.95 | 100 % | 0.60 |
| **mean** | **1.63** | 2.78 | 100 % | 0.49 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-reloc/poses/*.json --out runs/slam-5XXB-exam-reloc/shape.md`
