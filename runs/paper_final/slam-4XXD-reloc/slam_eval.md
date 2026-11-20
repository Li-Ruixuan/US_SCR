# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXD-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.5 / 8.2 | 3.3 | 0.24 | 2.0 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-418 | 4.09 | 6.12 | 100 % | 0.65 |
| run-419 | 3.69 | 5.82 | 100 % | 0.87 |
| run-420 | 4.26 | 5.89 | 100 % | 0.75 |
| run-421 | 5.59 | 7.92 | 100 % | 0.98 |
| run-423 | 4.48 | 5.71 | 100 % | 0.85 |
| run-424 | 4.63 | 5.99 | 100 % | 0.52 |
| **mean** | **4.46** | 6.24 | 100 % | 0.77 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXD-reloc/poses/*.json --out runs/paper_final/slam-4XXD-reloc/shape.md`
