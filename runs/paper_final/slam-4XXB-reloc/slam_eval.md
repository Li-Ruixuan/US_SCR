# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXB-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-403, room-404) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.7 / 6.6 | 3.2 | 0.25 | 1.9 / 4.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-409 | 2.21 | 3.39 | 100 % | 0.84 |
| run-410 | 4.31 | 5.07 | 100 % | 0.64 |
| run-411 | 3.82 | 5.25 | 100 % | 0.78 |
| run-412 | 4.44 | 5.80 | 100 % | 0.67 |
| **mean** | **3.70** | 4.88 | 100 % | 0.73 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXB-reloc/poses/*.json --out runs/paper_final/slam-4XXB-reloc/shape.md`
