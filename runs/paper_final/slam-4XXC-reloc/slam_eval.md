# RGB-D SLAM baseline: train_4XX (`runs/slam-4XXC-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-405, room-406) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.4 / 8.1 | 3.3 | 0.24 | 2.1 / 4.9 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-413 | 4.37 | 5.20 | 100 % | 0.57 |
| run-414 | 5.88 | 8.81 | 100 % | 0.65 |
| run-415 | 4.62 | 5.26 | 100 % | 0.54 |
| run-416 | 4.88 | 6.00 | 100 % | 0.67 |
| **mean** | **4.94** | 6.32 | 100 % | 0.61 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-4XXC-reloc/poses/*.json --out runs/paper_final/slam-4XXC-reloc/shape.md`
