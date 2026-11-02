# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2map-3XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **12.96** | 22.33 | 100 % | 1.394 | 2.01 |
| smoothed 0.25 s | **12.90** | 22.22 | 100 % | 0.662 | 1.66 |
| smoothed 0.5 s | **12.90** | 22.27 | 100 % | 0.663 | 1.71 |
| smoothed 1 s | **12.86** | 22.19 | 100 % | 0.477 | 1.49 |
| smoothed 2 s | **12.78** | 22.18 | 100 % | 0.459 | 1.39 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 8.3 (1.51) | 8.2 (1.17) | 8.2 (1.21) | 8.2 (1.00) | 8.2 (0.96) |
| run-314 | 15.8 (1.62) | 15.9 (1.20) | 15.8 (1.26) | 15.9 (1.00) | 15.8 (0.79) |
| run-315 | 10.4 (2.41) | 10.3 (2.09) | 10.3 (2.14) | 10.3 (1.97) | 10.5 (1.88) |
| run-316 | 11.3 (1.74) | 11.4 (1.42) | 11.4 (1.47) | 11.4 (1.27) | 11.2 (1.24) |
| run-317 | 18.9 (2.75) | 18.6 (2.39) | 18.7 (2.46) | 18.6 (2.20) | 18.2 (2.08) |
