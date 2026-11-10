# RGB-D SLAM baseline: test_5XXC (`runs/slam-5XXC-exam-occ60-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-507) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 3.4 / 6.4 | 1.8 | 0.23 | 1.3 / 3.4 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-517 | 1.92 | 6.47 | 100 % | 0.66 |
| run-518 | 2.21 | 6.06 | 100 % | 0.53 |
| run-519 | 2.51 | 31.78 | 100 % | 0.76 |
| run-520 | nan | nan | 0 % | nan |
| run-521 | nan | nan | 0 % | nan |
| run-522 | nan | nan | 0 % | nan |
| run-523 | nan | nan | 0 % | nan |
| run-524 | nan | nan | 0 % | nan |
| **mean** | **2.22** | 14.77 | 38 % | 0.65 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXC-exam-occ60-reloc/poses/*.json --out runs/slam-5XXC-exam-occ60-reloc/shape.md`
