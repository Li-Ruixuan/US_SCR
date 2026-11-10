# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.5 / 6.5 | 1.9 | 0.23 | 1.2 / 3.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.60 | 11.04 | 100 % | 1.97 |
| run-530 | 6.49 | 13.25 | 100 % | 3.00 |
| run-531 | 13.99 | 65.38 | 100 % | 7.76 |
| run-532 | 4.82 | 11.61 | 100 % | 2.64 |
| **mean** | **6.73** | 25.32 | 100 % | 3.84 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-oldC-reloc/poses/*.json --out runs/slam-5XXE-oldC-reloc/shape.md`
