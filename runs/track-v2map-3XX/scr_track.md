# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2map-3XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **50.62** | 55.79 | 100 % | 1.421 | 2.09 |
| smoothed 0.25 s | **50.57** | 55.65 | 100 % | 0.680 | 1.74 |
| smoothed 0.5 s | **50.58** | 55.67 | 100 % | 0.683 | 1.79 |
| smoothed 1 s | **50.54** | 55.65 | 100 % | 0.494 | 1.56 |
| smoothed 2 s | **50.56** | 55.64 | 100 % | 0.477 | 1.48 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 49.7 (1.56) | 49.6 (1.22) | 49.7 (1.26) | 49.6 (1.04) | 49.6 (1.03) |
| run-314 | 50.5 (1.68) | 50.6 (1.27) | 50.5 (1.33) | 50.5 (1.05) | 50.5 (0.84) |
| run-315 | 51.7 (2.45) | 51.7 (2.12) | 51.7 (2.18) | 51.8 (1.98) | 51.9 (1.88) |
| run-316 | 49.7 (1.90) | 49.8 (1.59) | 49.8 (1.65) | 49.7 (1.43) | 49.6 (1.40) |
| run-317 | 51.5 (2.84) | 51.2 (2.48) | 51.2 (2.53) | 51.1 (2.31) | 51.2 (2.25) |
