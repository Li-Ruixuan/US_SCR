# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-online/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 10.1 mm, 0.60 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 8.5 | 2.2 | 0.22 | 2.1 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.54 | 3.06 | 100 % | 0.56 |
| run-314 | 1.43 | 2.19 | 100 % | 0.44 |
| run-315 | 1.56 | 3.40 | 100 % | 0.94 |
| run-316 | 1.55 | 2.27 | 100 % | 0.78 |
| run-317 | 2.01 | 3.67 | 100 % | 1.05 |
| **mean** | **1.82** | 2.92 | 100 % | 0.75 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-3XX-online/poses/*.json --out runs/paper_final/slam-3XX-online/shape.md`
