# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-oldC-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.5 / 6.5 | 1.9 | 0.23 | 1.2 / 3.1 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.49 | 10.49 | 100 % | 1.33 |
| run-530 | 6.54 | 13.04 | 100 % | 1.75 |
| run-531 | 13.15 | 65.30 | 100 % | 6.63 |
| run-532 | 4.68 | 11.42 | 100 % | 1.58 |
| **mean** | **6.46** | 25.06 | 100 % | 2.82 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-oldC-reloc/poses/*.json --out runs/paper_final/slam-5XXE-oldC-reloc/shape.md`
