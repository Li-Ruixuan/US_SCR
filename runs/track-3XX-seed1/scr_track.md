# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX-seed1/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.11** | 4.11 | 100 % | 1.341 | 1.64 |
| smoothed 0.25 s | **2.00** | 3.94 | 100 % | 0.577 | 1.23 |
| smoothed 0.5 s | **2.01** | 3.95 | 100 % | 0.580 | 1.29 |
| smoothed 1 s | **1.98** | 3.85 | 100 % | 0.376 | 1.02 |
| smoothed 2 s | **1.95** | 3.84 | 100 % | 0.355 | 0.92 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 1.8 (1.33) | 1.7 (0.97) | 1.7 (1.01) | 1.6 (0.78) | 1.7 (0.73) |
| run-314 | 2.6 (1.55) | 2.6 (1.07) | 2.6 (1.13) | 2.6 (0.83) | 2.6 (0.63) |
| run-315 | 2.2 (1.89) | 2.0 (1.45) | 2.1 (1.53) | 2.0 (1.24) | 1.9 (1.12) |
| run-316 | 1.7 (1.55) | 1.6 (1.18) | 1.6 (1.24) | 1.6 (0.98) | 1.6 (0.91) |
| run-317 | 2.1 (1.91) | 2.0 (1.48) | 2.0 (1.56) | 2.0 (1.27) | 2.0 (1.23) |
