# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-oldB-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-504) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.1 / 6.4 | 1.8 | 0.21 | 1.2 / 3.5 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | nan | nan | 0 % | nan |
| run-518 | nan | nan | 0 % | nan |
| run-519 | nan | nan | 0 % | nan |
| run-520 | nan | nan | 0 % | nan |
| run-521 | 37.24 | 105.66 | 100 % | 2.14 |
| run-522 | nan | nan | 0 % | nan |
| run-523 | 14.01 | 33.95 | 100 % | 4.38 |
| run-524 | 8.66 | 32.55 | 100 % | 3.40 |
| **mean** | **19.97** | 57.39 | 38 % | 3.31 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-oldB-reloc/poses/*.json --out runs/slam-5XXC-oldB-reloc/shape.md`
