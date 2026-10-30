# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2conf-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.30** | 8.69 | 100 % | 1.406 | 1.74 |
| smoothed 0.25 s | **5.25** | 8.56 | 100 % | 0.619 | 1.33 |
| smoothed 0.5 s | **5.25** | 8.56 | 100 % | 0.608 | 1.38 |
| smoothed 1 s | **5.24** | 8.54 | 100 % | 0.390 | 1.11 |
| smoothed 2 s | **5.22** | 8.51 | 100 % | 0.354 | 1.00 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 4.1 (1.97) | 4.1 (1.53) | 4.0 (1.59) | 4.0 (1.34) | 4.0 (1.42) |
| run-402 | 6.3 (1.31) | 6.2 (0.95) | 6.2 (0.99) | 6.2 (0.77) | 6.2 (0.76) |
| run-403 | 5.3 (1.39) | 5.3 (1.02) | 5.3 (1.07) | 5.3 (0.80) | 5.4 (0.62) |
| run-404 | 8.7 (2.28) | 8.6 (1.80) | 8.6 (1.83) | 8.6 (1.34) | 8.5 (1.10) |
| run-405 | 5.6 (1.86) | 5.6 (1.40) | 5.6 (1.46) | 5.6 (1.17) | 5.6 (1.05) |
| run-406 | 3.3 (1.45) | 3.2 (1.10) | 3.2 (1.13) | 3.2 (0.94) | 3.2 (0.82) |
| run-407 | 4.2 (1.74) | 4.1 (1.36) | 4.1 (1.42) | 4.2 (1.19) | 4.1 (1.10) |
| run-408 | 4.8 (1.89) | 4.8 (1.48) | 4.8 (1.54) | 4.8 (1.30) | 4.8 (1.12) |
