# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX-scan20/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.12** | 5.70 | 100 % | 1.520 | 1.87 |
| smoothed 0.25 s | **3.03** | 5.48 | 100 % | 0.641 | 1.39 |
| smoothed 0.5 s | **3.05** | 5.54 | 100 % | 0.646 | 1.46 |
| smoothed 1 s | **3.00** | 5.39 | 100 % | 0.409 | 1.15 |
| smoothed 2 s | **3.00** | 5.33 | 100 % | 0.381 | 1.03 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 2.8 (1.45) | 2.7 (1.00) | 2.7 (1.05) | 2.7 (0.77) | 2.7 (0.70) |
| run-314 | 2.9 (1.61) | 2.8 (1.12) | 2.8 (1.18) | 2.8 (0.88) | 2.9 (0.65) |
| run-315 | 3.8 (2.44) | 3.8 (1.88) | 3.9 (1.95) | 3.8 (1.60) | 3.8 (1.42) |
| run-316 | 2.9 (1.63) | 2.8 (1.24) | 2.8 (1.31) | 2.7 (1.04) | 2.7 (1.02) |
| run-317 | 3.1 (2.22) | 3.0 (1.73) | 3.0 (1.82) | 2.9 (1.48) | 2.9 (1.38) |
