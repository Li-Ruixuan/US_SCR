# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.21** | 8.22 | 100 % | 1.420 | 1.75 |
| smoothed 0.25 s | **5.18** | 8.00 | 100 % | 0.605 | 1.32 |
| smoothed 0.5 s | **5.18** | 8.00 | 100 % | 0.601 | 1.37 |
| smoothed 1 s | **5.15** | 7.94 | 100 % | 0.386 | 1.09 |
| smoothed 2 s | **5.14** | 7.94 | 100 % | 0.352 | 0.99 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 4.1 (1.95) | 4.1 (1.50) | 4.1 (1.56) | 4.0 (1.33) | 4.0 (1.42) |
| run-402 | 6.3 (1.33) | 6.3 (0.95) | 6.3 (0.99) | 6.3 (0.78) | 6.3 (0.74) |
| run-403 | 5.5 (1.37) | 5.5 (0.99) | 5.5 (1.04) | 5.5 (0.79) | 5.5 (0.62) |
| run-404 | 8.8 (2.38) | 8.8 (1.75) | 8.7 (1.81) | 8.8 (1.28) | 8.7 (1.08) |
| run-405 | 6.1 (1.85) | 6.0 (1.39) | 6.0 (1.46) | 6.1 (1.16) | 6.0 (1.04) |
| run-406 | 2.9 (1.49) | 2.8 (1.14) | 2.8 (1.17) | 2.8 (0.97) | 2.8 (0.84) |
| run-407 | 3.9 (1.71) | 3.9 (1.34) | 3.9 (1.40) | 3.9 (1.17) | 3.9 (1.08) |
| run-408 | 4.0 (1.91) | 4.0 (1.47) | 4.0 (1.53) | 3.9 (1.27) | 3.9 (1.10) |
