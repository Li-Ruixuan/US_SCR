# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.5 | 1.3 | 0.25 | 0.8 / 1.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.11 | 2.10 | 100 % | 0.41 |
| run-530 | 2.54 | 3.67 | 100 % | 0.45 |
| run-531 | 2.92 | 4.78 | 100 % | 0.65 |
| run-532 | 2.34 | 3.83 | 100 % | 0.47 |
| **mean** | **2.23** | 3.60 | 100 % | 0.49 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXE-exam-reloc/poses/*.json --out runs/slam-5XXE-exam-reloc/shape.md`
