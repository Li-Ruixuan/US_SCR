# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ30-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 1.9 | 0.24 | 1.2 / 3.3 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.80 | 2.46 | 100 % | 0.40 |
| run-518 | 1.96 | 2.77 | 100 % | 0.33 |
| run-519 | 1.94 | 2.81 | 100 % | 0.40 |
| run-520 | 1.84 | 3.44 | 100 % | 0.56 |
| run-521 | 2.22 | 3.28 | 100 % | 0.44 |
| run-522 | 2.04 | 3.41 | 100 % | 0.40 |
| run-523 | 2.24 | 3.91 | 100 % | 0.73 |
| run-524 | 1.98 | 3.41 | 100 % | 0.48 |
| **mean** | **2.00** | 3.19 | 100 % | 0.47 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXC-exam-occ30-reloc/poses/*.json --out runs/paper_final/slam-5XXC-exam-occ30-reloc/shape.md`
