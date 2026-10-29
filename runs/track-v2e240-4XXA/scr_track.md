# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2e240-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.32** | 8.21 | 100 % | 1.374 | 1.70 |
| smoothed 0.25 s | **5.29** | 8.17 | 100 % | 0.590 | 1.29 |
| smoothed 0.5 s | **5.28** | 8.18 | 100 % | 0.591 | 1.35 |
| smoothed 1 s | **5.29** | 8.15 | 100 % | 0.384 | 1.09 |
| smoothed 2 s | **5.28** | 8.10 | 100 % | 0.352 | 0.99 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 4.3 (1.91) | 4.2 (1.49) | 4.2 (1.55) | 4.2 (1.31) | 4.3 (1.41) |
| run-402 | 6.5 (1.25) | 6.5 (0.91) | 6.5 (0.94) | 6.5 (0.73) | 6.5 (0.73) |
| run-403 | 5.4 (1.33) | 5.5 (0.98) | 5.5 (1.03) | 5.5 (0.79) | 5.5 (0.62) |
| run-404 | 9.2 (2.30) | 9.2 (1.68) | 9.2 (1.74) | 9.2 (1.33) | 9.2 (1.10) |
| run-405 | 6.5 (1.80) | 6.5 (1.39) | 6.5 (1.45) | 6.5 (1.17) | 6.4 (1.08) |
| run-406 | 2.3 (1.43) | 2.2 (1.10) | 2.2 (1.14) | 2.2 (0.94) | 2.2 (0.82) |
| run-407 | 4.1 (1.74) | 4.1 (1.38) | 4.1 (1.44) | 4.1 (1.19) | 4.0 (1.11) |
| run-408 | 4.2 (1.86) | 4.2 (1.43) | 4.1 (1.48) | 4.1 (1.24) | 4.1 (1.08) |
