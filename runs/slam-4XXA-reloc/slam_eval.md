# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXA-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-401, room-402) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 5.1 / 11.6 | 4.9 | 0.33 | 4.1 / 10.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-401 | 4.36 | 5.78 | 100 % | 1.15 |
| run-402 | 3.35 | 4.03 | 100 % | 0.59 |
| run-403 | 3.46 | 4.35 | 100 % | 0.52 |
| run-404 | 3.90 | 4.55 | 100 % | 0.79 |
| run-405 | 3.37 | 5.32 | 100 % | 0.89 |
| run-406 | 5.50 | 6.05 | 100 % | 0.71 |
| run-407 | 4.35 | 5.60 | 100 % | 0.80 |
| run-408 | 4.81 | 6.20 | 100 % | 0.90 |
| **mean** | **4.14** | 5.23 | 100 % | 0.79 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXA-reloc/poses/*.json --out runs/slam-4XXA-reloc/shape.md`
