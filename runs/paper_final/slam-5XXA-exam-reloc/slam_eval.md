# RGB-D SLAM baseline: test_5XXA (`runs/slam-5XXA-exam-reloc/online.txt`)

One alignment of the session and the camera calibration (fixed from `runs/slam-3XX/slam_eval.json`) from the room-scan frames (room-502) against Polaris; the sweeps are not used for the fit. Smoothing: 2 s.

| room scan: frames with a pose | scene points at 1 m (median / p90) | camera position | rotation | 1 s motion (median / p90) |
|---|---|---|---|---|
| 100 % | 4.0 / 9.2 | 4.1 | 0.39 | 1.5 / 4.7 |

| sweep | US image median | p90 | frames with a pose | step, 8 rows |
|---|---|---|---|---|
| run-501 | 2.92 | 4.91 | 100 % | 0.40 |
| run-502 | 3.26 | 4.96 | 100 % | 0.50 |
| run-503 | 3.40 | 4.74 | 100 % | 0.40 |
| run-504 | 4.38 | 6.23 | 100 % | 0.62 |
| run-505 | 4.09 | 5.26 | 100 % | 0.58 |
| run-506 | 3.76 | 4.81 | 100 % | 0.44 |
| run-507 | 5.45 | 6.44 | 100 % | 0.34 |
| run-508 | 3.96 | 5.06 | 100 % | 0.34 |
| **mean** | **3.90** | 5.30 | 100 % | 0.45 |

Shape: `python tools/us_analysis.py shape --json runs/paper_final/slam-5XXA-exam-reloc/poses/*.json --out runs/paper_final/slam-5XXA-exam-reloc/shape.md`
