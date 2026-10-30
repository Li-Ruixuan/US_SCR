# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2conf-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.27** | 9.24 | 100 % | 1.105 | 1.59 |
| smoothed 0.25 s | **5.27** | 9.21 | 100 % | 0.543 | 1.31 |
| smoothed 0.5 s | **5.28** | 9.21 | 100 % | 0.549 | 1.35 |
| smoothed 1 s | **5.27** | 9.13 | 100 % | 0.403 | 1.17 |
| smoothed 2 s | **5.28** | 9.07 | 100 % | 0.379 | 1.11 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 5.0 (1.94) | 4.9 (1.56) | 5.0 (1.62) | 4.9 (1.41) | 5.0 (1.51) |
| run-402 | 5.9 (1.28) | 6.0 (0.99) | 6.0 (1.03) | 6.0 (0.85) | 6.0 (0.82) |
| run-403 | 4.1 (1.17) | 4.0 (0.93) | 4.0 (0.97) | 4.1 (0.78) | 4.0 (0.66) |
| run-404 | 7.5 (1.93) | 7.5 (1.63) | 7.5 (1.67) | 7.5 (1.44) | 7.5 (1.31) |
| run-405 | 6.4 (1.74) | 6.4 (1.41) | 6.4 (1.47) | 6.4 (1.24) | 6.4 (1.17) |
| run-406 | 5.6 (1.31) | 5.6 (1.08) | 5.6 (1.10) | 5.6 (0.98) | 5.7 (0.90) |
| run-407 | 3.1 (1.76) | 3.1 (1.52) | 3.1 (1.56) | 3.1 (1.45) | 3.1 (1.39) |
| run-408 | 4.6 (1.61) | 4.6 (1.37) | 4.6 (1.41) | 4.6 (1.24) | 4.5 (1.10) |
