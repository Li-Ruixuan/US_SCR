# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 6.6 | 3.2 | 0.25 | 1.9 / 4.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 2.21 | 3.41 | 100 % | 0.76 |
| run-410 | 4.31 | 4.99 | 100 % | 0.68 |
| run-411 | 3.85 | 5.28 | 100 % | 0.94 |
| run-412 | 4.45 | 5.83 | 100 % | 0.75 |
| **mean** | **3.70** | 4.88 | 100 % | 0.78 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXB-reloc/poses/*.json --out runs/slam-4XXB-reloc/shape.md`
