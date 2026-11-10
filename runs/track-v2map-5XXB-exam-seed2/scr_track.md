# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXB-exam-seed2/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **4.03** | 7.59 | 100 % | 1.065 | 1.36 |
| smoothed 0.25 s | **4.00** | 7.52 | 100 % | 0.480 | 1.06 |
| smoothed 0.5 s | **4.00** | 7.53 | 100 % | 0.478 | 1.10 |
| smoothed 1 s | **3.98** | 7.53 | 100 % | 0.290 | 0.87 |
| smoothed 2 s | **3.97** | 7.45 | 100 % | 0.241 | 0.71 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | 3.8 (1.26) | 3.8 (0.97) | 3.8 (1.02) | 3.8 (0.79) | 3.8 (0.68) |
| run-510 | 4.0 (1.24) | 4.0 (0.90) | 4.0 (0.95) | 3.9 (0.71) | 3.9 (0.54) |
| run-511 | 3.0 (1.09) | 2.9 (0.76) | 2.9 (0.80) | 2.9 (0.59) | 2.9 (0.44) |
| run-512 | 5.9 (1.79) | 5.8 (1.37) | 5.8 (1.41) | 5.8 (1.02) | 5.8 (0.75) |
| run-513 | 3.4 (1.32) | 3.3 (1.01) | 3.3 (1.06) | 3.4 (0.82) | 3.3 (0.62) |
| run-514 | 4.1 (1.61) | 4.1 (1.36) | 4.1 (1.42) | 4.1 (1.19) | 4.1 (1.05) |
| run-515 | 4.4 (1.12) | 4.4 (0.93) | 4.4 (0.96) | 4.4 (0.82) | 4.4 (0.74) |
| run-516 | 3.7 (1.46) | 3.7 (1.16) | 3.7 (1.21) | 3.7 (0.99) | 3.7 (0.84) |
