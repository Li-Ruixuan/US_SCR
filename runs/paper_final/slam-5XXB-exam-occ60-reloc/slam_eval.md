# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ60-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.7 | 0.22 | 1.1 / 2.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.57 | 3.42 | 100 % | 0.76 |
| run-510 | 1.91 | 5.83 | 100 % | 1.15 |
| run-511 | 1.84 | 5.50 | 100 % | 0.73 |
| run-512 | 3.10 | 7.97 | 100 % | 1.19 |
| run-513 | 1.74 | 3.35 | 100 % | 0.64 |
| run-514 | 1.84 | 3.46 | 100 % | 0.83 |
| run-515 | 2.03 | 3.36 | 100 % | 1.09 |
| run-516 | 39.73 | 119.69 | 100 % | 2.20 |
| **mean** | **6.72** | 19.07 | 100 % | 1.07 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXB-exam-occ60-reloc/poses/*.json --out runs/paper_final/slam-5XXB-exam-occ60-reloc/shape.md`
