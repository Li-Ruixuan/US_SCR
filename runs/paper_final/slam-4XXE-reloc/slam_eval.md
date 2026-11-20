# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXE-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.1 | 3.2 | 0.24 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-425 | 4.73 | 5.56 | 100 % | 1.32 |
| run-426 | 4.36 | 5.21 | 100 % | 1.23 |
| run-427 | 6.86 | 8.45 | 100 % | 0.90 |
| run-428 | 4.19 | 6.29 | 100 % | 0.78 |
| **mean** | **5.03** | 6.38 | 100 % | 1.06 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXE-reloc/poses/*.json --out runs/paper_final/slam-4XXE-reloc/shape.md`
