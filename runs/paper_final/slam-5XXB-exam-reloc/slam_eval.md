# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.7 | 0.21 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.47 | 2.54 | 100 % | 0.52 |
| run-510 | 1.72 | 2.56 | 100 % | 0.39 |
| run-511 | 1.21 | 1.89 | 100 % | 0.32 |
| run-512 | 2.69 | 4.37 | 100 % | 0.47 |
| run-513 | 1.04 | 2.38 | 100 % | 0.42 |
| run-514 | 1.44 | 2.69 | 100 % | 0.66 |
| run-515 | 1.90 | 2.79 | 100 % | 0.45 |
| run-516 | 1.49 | 3.03 | 100 % | 0.59 |
| **mean** | **1.62** | 2.78 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-reloc/poses/*.json --out runs/paper_final/slam-5XXB-exam-reloc/shape.md`
