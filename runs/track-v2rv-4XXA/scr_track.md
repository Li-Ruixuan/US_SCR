# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2rv-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.08** | 8.52 | 100 % | 1.419 | 1.75 |
| smoothed 0.25 s | **5.00** | 8.35 | 100 % | 0.605 | 1.31 |
| smoothed 0.5 s | **5.01** | 8.35 | 100 % | 0.605 | 1.37 |
| smoothed 1 s | **4.98** | 8.32 | 100 % | 0.387 | 1.10 |
| smoothed 2 s | **4.98** | 8.23 | 100 % | 0.351 | 0.98 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 4.1 (2.04) | 4.1 (1.59) | 4.1 (1.64) | 4.1 (1.37) | 4.1 (1.45) |
| run-402 | 6.2 (1.35) | 6.2 (0.96) | 6.2 (1.01) | 6.2 (0.77) | 6.1 (0.73) |
| run-403 | 5.1 (1.39) | 5.1 (1.02) | 5.1 (1.06) | 5.1 (0.81) | 5.1 (0.65) |
| run-404 | 8.3 (2.21) | 8.1 (1.53) | 8.1 (1.59) | 8.0 (1.22) | 8.1 (1.03) |
| run-405 | 5.9 (1.95) | 5.8 (1.45) | 5.8 (1.52) | 5.8 (1.20) | 5.8 (1.10) |
| run-406 | 2.5 (1.53) | 2.3 (1.20) | 2.4 (1.24) | 2.3 (1.00) | 2.2 (0.83) |
| run-407 | 4.1 (1.60) | 4.0 (1.31) | 4.0 (1.35) | 4.0 (1.15) | 4.0 (1.07) |
| run-408 | 4.5 (1.90) | 4.4 (1.47) | 4.4 (1.53) | 4.4 (1.25) | 4.4 (1.03) |
