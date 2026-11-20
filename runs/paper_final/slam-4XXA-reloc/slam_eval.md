# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.1 / 11.6 | 4.9 | 0.33 | 4.1 / 10.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 4.39 | 5.94 | 100 % | 1.35 |
| run-402 | 3.36 | 4.05 | 100 % | 0.63 |
| run-403 | 3.46 | 4.35 | 100 % | 0.47 |
| run-404 | 3.91 | 4.53 | 100 % | 0.71 |
| run-405 | 3.33 | 5.43 | 100 % | 0.87 |
| run-406 | 5.53 | 6.02 | 100 % | 0.64 |
| run-407 | 4.31 | 5.66 | 100 % | 0.74 |
| run-408 | 4.79 | 6.13 | 100 % | 0.74 |
| **mean** | **4.13** | 5.26 | 100 % | 0.77 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXA-reloc/poses/*.json --out runs/paper_final/slam-4XXA-reloc/shape.md`
