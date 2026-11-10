# RGB-D SLAM baseline: train_3XX (`runs/slam-3XX-reloc/online.txt`)

One alignment of the session and the camera calibration (fitted on the room scan: 9.8 mm, 0.59 deg) from the room-scan frames (room-301, room-302) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.6 / 8.5 | 2.2 | 0.22 | 2.2 / 5.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-313 | 2.39 | 2.90 | 100 % | 0.57 |
| run-314 | 1.34 | 2.02 | 100 % | 0.51 |
| run-315 | 1.69 | 3.50 | 100 % | 0.96 |
| run-316 | 1.09 | 2.04 | 100 % | 0.66 |
| run-317 | 2.10 | 5.22 | 100 % | 1.07 |
| **mean** | **1.72** | 3.14 | 100 % | 0.76 |

Shape: `python tools/us_analysis.py shape --json runs/slam-3XX-reloc/poses/*.json --out runs/slam-3XX-reloc/shape.md`
