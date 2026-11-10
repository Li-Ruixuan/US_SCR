# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ60-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.9 / 7.1 | 1.7 | 0.22 | 1.1 / 2.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.61 | 3.52 | 100 % | 0.83 |
| run-510 | 1.91 | 5.93 | 100 % | 1.30 |
| run-511 | 1.81 | 5.95 | 100 % | 0.88 |
| run-512 | 3.08 | 8.30 | 100 % | 1.29 |
| run-513 | 1.74 | 3.41 | 100 % | 0.73 |
| run-514 | 1.83 | 3.57 | 100 % | 0.91 |
| run-515 | 2.03 | 3.46 | 100 % | 1.10 |
| run-516 | 39.73 | 119.69 | 100 % | 2.23 |
| **mean** | **6.72** | 19.23 | 100 % | 1.16 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ60-reloc/poses/*.json --out runs/slam-5XXB-exam-occ60-reloc/shape.md`
