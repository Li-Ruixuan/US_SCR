# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.2 | 3.3 | 0.24 | 2.0 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.11 | 6.10 | 100 % | 0.68 |
| run-419 | 3.70 | 5.56 | 100 % | 0.83 |
| run-420 | 4.21 | 5.91 | 100 % | 0.92 |
| run-421 | 5.57 | 7.92 | 100 % | 0.97 |
| run-423 | 4.48 | 5.69 | 100 % | 1.00 |
| run-424 | 4.57 | 5.98 | 100 % | 0.59 |
| **mean** | **4.44** | 6.19 | 100 % | 0.83 |

Shape: `python tools/us_analysis.py shape --json runs/slam-4XXD-reloc/poses/*.json --out runs/slam-4XXD-reloc/shape.md`
