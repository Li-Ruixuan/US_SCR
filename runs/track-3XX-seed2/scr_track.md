# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX-seed2/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.20** | 4.04 | 100 % | 1.341 | 1.64 |
| smoothed 0.25 s | **2.14** | 3.85 | 100 % | 0.576 | 1.23 |
| smoothed 0.5 s | **2.15** | 3.85 | 100 % | 0.581 | 1.30 |
| smoothed 1 s | **2.11** | 3.76 | 100 % | 0.376 | 1.02 |
| smoothed 2 s | **2.12** | 3.73 | 100 % | 0.356 | 0.93 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 2.0 (1.32) | 1.9 (0.96) | 1.9 (1.01) | 1.9 (0.78) | 1.8 (0.72) |
| run-314 | 2.7 (1.52) | 2.8 (1.07) | 2.8 (1.14) | 2.7 (0.83) | 2.8 (0.63) |
| run-315 | 2.3 (1.88) | 2.1 (1.44) | 2.1 (1.52) | 2.1 (1.24) | 2.1 (1.13) |
| run-316 | 1.7 (1.56) | 1.6 (1.19) | 1.6 (1.26) | 1.6 (1.00) | 1.6 (0.95) |
| run-317 | 2.3 (1.94) | 2.3 (1.48) | 2.3 (1.56) | 2.3 (1.27) | 2.3 (1.23) |
