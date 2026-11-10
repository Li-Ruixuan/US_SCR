# RGB-D SLAM baseline: test_5XXD (`runs/slam-5XXD-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.3 / 6.5 | 1.7 | 0.23 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-525 | 2.14 | 3.08 | 100 % | 0.56 |
| run-526 | 1.48 | 2.69 | 100 % | 0.68 |
| run-527 | 1.46 | 2.96 | 100 % | 0.85 |
| run-528 | 1.43 | 2.64 | 100 % | 0.84 |
| **mean** | **1.63** | 2.84 | 100 % | 0.73 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXD-exam-reloc/poses/*.json --out runs/slam-5XXD-exam-reloc/shape.md`
