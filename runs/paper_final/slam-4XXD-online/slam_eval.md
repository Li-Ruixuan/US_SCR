# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-online/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.2 | 3.2 | 0.24 | 2.0 / 5.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.85 | 6.48 | 100 % | 0.64 |
| run-419 | 4.11 | 6.12 | 100 % | 0.82 |
| run-420 | 5.26 | 6.54 | 100 % | 0.62 |
| run-421 | 5.11 | 7.96 | 100 % | 0.90 |
| run-423 | 4.30 | 4.92 | 100 % | 0.69 |
| run-424 | 4.47 | 5.49 | 100 % | 0.44 |
| **mean** | **4.68** | 6.25 | 100 % | 0.68 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXD-online/poses/*.json --out runs/paper_final/slam-4XXD-online/shape.md`
