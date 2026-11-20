# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-generic-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-501) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.6 / 8.9 | 3.1 | 0.32 | 2.4 / 6.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.89 | 4.21 | 100 % | 0.42 |
| run-502 | 3.32 | 4.85 | 100 % | 0.54 |
| run-503 | 3.20 | 4.01 | 100 % | 0.44 |
| run-504 | 2.92 | 4.32 | 100 % | 0.63 |
| run-505 | 2.76 | 3.94 | 100 % | 0.64 |
| run-506 | 2.44 | 3.70 | 100 % | 0.45 |
| run-507 | 2.17 | 2.72 | 100 % | 0.35 |
| run-508 | 2.42 | 3.51 | 100 % | 0.37 |
| **mean** | **2.76** | 3.91 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-generic-reloc/poses/*.json --out runs/paper_final/slam-5XXA-generic-reloc/shape.md`
