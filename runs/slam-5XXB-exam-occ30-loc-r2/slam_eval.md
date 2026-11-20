# RGB-D SLAM baseline: test_5XXB (`runs/slam-5XXB-exam-occ30-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-505) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.8 / 7.2 | 1.6 | 0.22 | 1.1 / 3.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-509 | 1.38 | 3.41 | 100 % | 0.59 |
| run-510 | 1.89 | 4.54 | 100 % | 0.55 |
| run-511 | 1.66 | 2.94 | 100 % | 0.42 |
| run-512 | 127.73 | 132.38 | 100 % | 1.47 |
| run-513 | 1.28 | 3.22 | 100 % | 0.51 |
| run-514 | 1.54 | 2.94 | 100 % | 0.73 |
| run-515 | 1.87 | 3.21 | 100 % | 0.62 |
| run-516 | 1.74 | 3.08 | 100 % | 0.67 |
| **mean** | **17.39** | 19.46 | 100 % | 0.70 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXB-exam-occ30-loc-r2/poses/*.json --out runs/slam-5XXB-exam-occ30-loc-r2/shape.md`
