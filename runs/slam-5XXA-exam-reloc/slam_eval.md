# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 1 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.0 / 9.2 | 4.1 | 0.39 | 1.5 / 4.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.93 | 4.90 | 100 % | 0.45 |
| run-502 | 3.25 | 4.89 | 100 % | 0.49 |
| run-503 | 3.38 | 4.74 | 100 % | 0.43 |
| run-504 | 4.40 | 6.25 | 100 % | 0.64 |
| run-505 | 4.09 | 5.09 | 100 % | 0.64 |
| run-506 | 3.79 | 4.84 | 100 % | 0.45 |
| run-507 | 5.44 | 6.44 | 100 % | 0.40 |
| run-508 | 3.96 | 4.99 | 100 % | 0.37 |
| **mean** | **3.90** | 5.27 | 100 % | 0.48 |

Shape: `python tools/us_analysis.py shape --json runs/slam-5XXA-exam-reloc/poses/*.json --out runs/slam-5XXA-exam-reloc/shape.md`
