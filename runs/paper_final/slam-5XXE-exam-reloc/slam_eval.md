# RGB-D SLAM baseline: test_5XXE (`runs/slam-5XXE-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-509) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 2.9 / 5.5 | 1.3 | 0.25 | 0.8 / 1.8 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-529 | 1.13 | 2.12 | 100 % | 0.38 |
| run-530 | 2.54 | 3.75 | 100 % | 0.36 |
| run-531 | 2.87 | 4.64 | 100 % | 0.59 |
| run-532 | 2.35 | 3.84 | 100 % | 0.44 |
| **mean** | **2.22** | 3.58 | 100 % | 0.44 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXE-exam-reloc/poses/*.json --out runs/paper_final/slam-5XXE-exam-reloc/shape.md`
