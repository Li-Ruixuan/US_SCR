# Single-model tracking: SCR alone on every 2th row (test_4XXC, `runs/v2pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **4.03** | 8.62 | 100 % | 1.083 | 1.33 |
| smoothed 0.25 s | **4.00** | 8.59 | 100 % | 0.463 | 1.01 |
| smoothed 0.5 s | **4.01** | 8.57 | 100 % | 0.470 | 1.05 |
| smoothed 1 s | **3.99** | 8.63 | 100 % | 0.304 | 0.84 |
| smoothed 2 s | **3.98** | 8.54 | 100 % | 0.291 | 0.79 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-413 | 3.0 (1.22) | 3.0 (0.89) | 3.0 (0.93) | 3.0 (0.71) | 3.0 (0.64) |
| run-414 | 4.4 (1.21) | 4.4 (0.93) | 4.4 (0.97) | 4.4 (0.80) | 4.4 (0.78) |
| run-415 | 4.5 (1.40) | 4.5 (1.01) | 4.5 (1.06) | 4.5 (0.81) | 4.5 (0.74) |
| run-416 | 4.2 (1.51) | 4.1 (1.19) | 4.2 (1.24) | 4.1 (1.03) | 4.1 (0.99) |
