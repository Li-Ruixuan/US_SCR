# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.03** | 3.77 | 100 % | 1.345 | 1.67 |
| smoothed 0.25 s | **1.91** | 3.58 | 100 % | 0.584 | 1.25 |
| smoothed 0.5 s | **1.93** | 3.61 | 100 % | 0.589 | 1.32 |
| smoothed 1 s | **1.89** | 3.49 | 100 % | 0.380 | 1.04 |
| smoothed 2 s | **1.85** | 3.41 | 100 % | 0.355 | 0.93 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 1.8 (1.35) | 1.7 (0.99) | 1.8 (1.04) | 1.7 (0.79) | 1.7 (0.71) |
| run-314 | 2.3 (1.55) | 2.2 (1.09) | 2.2 (1.15) | 2.1 (0.87) | 2.1 (0.65) |
| run-315 | 2.2 (1.91) | 2.0 (1.47) | 2.1 (1.55) | 2.0 (1.27) | 2.0 (1.12) |
| run-316 | 1.6 (1.58) | 1.5 (1.20) | 1.5 (1.27) | 1.5 (0.98) | 1.4 (0.91) |
| run-317 | 2.3 (1.94) | 2.1 (1.50) | 2.1 (1.58) | 2.1 (1.28) | 2.1 (1.26) |
