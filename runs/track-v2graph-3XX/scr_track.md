# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2graph-3XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **12.50** | 14.78 | 100 % | 1.404 | 1.86 |
| smoothed 0.25 s | **12.50** | 14.64 | 100 % | 0.631 | 1.46 |
| smoothed 0.5 s | **12.51** | 14.66 | 100 % | 0.638 | 1.52 |
| smoothed 1 s | **12.52** | 14.58 | 100 % | 0.425 | 1.25 |
| smoothed 2 s | **12.49** | 14.55 | 100 % | 0.400 | 1.14 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 12.1 (1.43) | 12.1 (1.05) | 12.1 (1.11) | 12.1 (0.86) | 12.1 (0.77) |
| run-314 | 11.5 (1.71) | 11.5 (1.23) | 11.5 (1.29) | 11.5 (0.99) | 11.4 (0.74) |
| run-315 | 11.7 (2.02) | 11.7 (1.63) | 11.7 (1.71) | 11.6 (1.42) | 11.6 (1.30) |
| run-316 | 11.7 (1.74) | 11.7 (1.38) | 11.7 (1.45) | 11.7 (1.20) | 11.7 (1.14) |
| run-317 | 15.5 (2.38) | 15.6 (1.98) | 15.6 (2.05) | 15.7 (1.79) | 15.6 (1.74) |
