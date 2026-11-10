# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXB-exam-seed1/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **4.20** | 7.67 | 100 % | 1.043 | 1.33 |
| smoothed 0.25 s | **4.17** | 7.60 | 100 % | 0.475 | 1.04 |
| smoothed 0.5 s | **4.17** | 7.60 | 100 % | 0.468 | 1.07 |
| smoothed 1 s | **4.18** | 7.60 | 100 % | 0.284 | 0.85 |
| smoothed 2 s | **4.18** | 7.58 | 100 % | 0.240 | 0.70 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | 4.1 (1.29) | 4.0 (1.00) | 4.0 (1.05) | 4.0 (0.81) | 4.0 (0.68) |
| run-510 | 4.4 (1.22) | 4.3 (0.88) | 4.3 (0.92) | 4.4 (0.70) | 4.3 (0.54) |
| run-511 | 3.1 (1.09) | 3.1 (0.78) | 3.1 (0.82) | 3.1 (0.60) | 3.1 (0.46) |
| run-512 | 6.0 (1.55) | 5.9 (1.19) | 5.9 (1.19) | 6.0 (0.88) | 6.0 (0.69) |
| run-513 | 3.5 (1.31) | 3.5 (1.00) | 3.5 (1.04) | 3.6 (0.80) | 3.6 (0.61) |
| run-514 | 4.2 (1.58) | 4.2 (1.33) | 4.1 (1.38) | 4.1 (1.17) | 4.1 (1.03) |
| run-515 | 4.5 (1.15) | 4.5 (0.95) | 4.5 (0.98) | 4.6 (0.85) | 4.5 (0.76) |
| run-516 | 3.8 (1.46) | 3.7 (1.16) | 3.8 (1.21) | 3.7 (1.02) | 3.7 (0.86) |
