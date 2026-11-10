# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-loc-r2/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.3 / 8.1 | 3.3 | 0.25 | 2.0 / 4.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.27 | 6.03 | 100 % | 0.64 |
| run-419 | 3.65 | 6.59 | 100 % | 0.70 |
| run-420 | 4.87 | 6.52 | 100 % | 0.81 |
| run-421 | 6.45 | 14.58 | 100 % | 0.96 |
| run-423 | 4.37 | 5.07 | 100 % | 0.62 |
| run-424 | 4.40 | 4.91 | 100 % | 0.43 |
| **mean** | **4.67** | 7.28 | 100 % | 0.69 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXD-loc-r2/poses/*.json --out runs/slam-4XXD-loc-r2/shape.md`
