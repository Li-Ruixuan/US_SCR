# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX-scan40/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.17** | 4.36 | 100 % | 1.391 | 1.68 |
| smoothed 0.25 s | **2.05** | 4.16 | 100 % | 0.589 | 1.25 |
| smoothed 0.5 s | **2.05** | 4.18 | 100 % | 0.596 | 1.31 |
| smoothed 1 s | **2.02** | 4.10 | 100 % | 0.380 | 1.04 |
| smoothed 2 s | **2.03** | 4.06 | 100 % | 0.359 | 0.94 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 2.0 (1.37) | 1.9 (0.95) | 1.9 (1.01) | 1.9 (0.75) | 1.8 (0.69) |
| run-314 | 2.6 (1.51) | 2.6 (1.05) | 2.5 (1.11) | 2.6 (0.82) | 2.6 (0.63) |
| run-315 | 2.1 (1.90) | 1.9 (1.47) | 1.9 (1.54) | 1.9 (1.27) | 1.9 (1.11) |
| run-316 | 1.8 (1.60) | 1.7 (1.21) | 1.7 (1.27) | 1.6 (1.03) | 1.6 (0.98) |
| run-317 | 2.4 (2.01) | 2.2 (1.55) | 2.2 (1.63) | 2.2 (1.32) | 2.2 (1.29) |
