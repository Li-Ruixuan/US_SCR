# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-generic-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-501) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.6 / 8.9 | 3.1 | 0.32 | 2.4 / 6.0 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.92 | 4.27 | 100 % | 0.48 |
| run-502 | 3.34 | 4.88 | 100 % | 0.60 |
| run-503 | 3.19 | 4.03 | 100 % | 0.53 |
| run-504 | 2.90 | 4.27 | 100 % | 0.68 |
| run-505 | 2.73 | 3.95 | 100 % | 0.74 |
| run-506 | 2.45 | 3.71 | 100 % | 0.50 |
| run-507 | 2.14 | 2.75 | 100 % | 0.43 |
| run-508 | 2.41 | 3.50 | 100 % | 0.46 |
| **mean** | **2.76** | 3.92 | 100 % | 0.55 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-generic-reloc/poses/*.json --out runs/slam-5XXA-generic-reloc/shape.md`
