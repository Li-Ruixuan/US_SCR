# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX-room301/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.12** | 5.64 | 100 % | 1.474 | 1.94 |
| smoothed 0.25 s | **2.97** | 5.45 | 100 % | 0.669 | 1.52 |
| smoothed 0.5 s | **2.98** | 5.48 | 100 % | 0.675 | 1.59 |
| smoothed 1 s | **2.92** | 5.34 | 100 % | 0.462 | 1.30 |
| smoothed 2 s | **2.98** | 5.34 | 100 % | 0.442 | 1.18 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-315 | 3.8 (2.06) | 3.6 (1.65) | 3.6 (1.72) | 3.6 (1.43) | 3.7 (1.23) |
| run-316 | 2.5 (1.64) | 2.4 (1.24) | 2.4 (1.31) | 2.3 (1.02) | 2.4 (0.94) |
| run-317 | 3.0 (2.13) | 3.0 (1.67) | 3.0 (1.75) | 2.9 (1.44) | 2.9 (1.35) |
