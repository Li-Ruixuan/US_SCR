# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2rvf-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.01** | 7.65 | 100 % | 1.379 | 1.71 |
| smoothed 0.25 s | **4.96** | 7.50 | 100 % | 0.599 | 1.31 |
| smoothed 0.5 s | **4.97** | 7.51 | 100 % | 0.601 | 1.36 |
| smoothed 1 s | **4.93** | 7.48 | 100 % | 0.385 | 1.09 |
| smoothed 2 s | **4.94** | 7.48 | 100 % | 0.348 | 0.97 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 4.5 (2.01) | 4.4 (1.56) | 4.5 (1.62) | 4.4 (1.36) | 4.4 (1.43) |
| run-402 | 6.1 (1.24) | 6.1 (0.90) | 6.0 (0.94) | 6.0 (0.74) | 6.1 (0.72) |
| run-403 | 4.6 (1.41) | 4.7 (1.03) | 4.7 (1.08) | 4.7 (0.81) | 4.7 (0.63) |
| run-404 | 6.8 (2.03) | 6.6 (1.49) | 6.6 (1.59) | 6.6 (1.16) | 6.6 (0.95) |
| run-405 | 6.1 (1.96) | 6.0 (1.50) | 6.0 (1.57) | 6.0 (1.26) | 6.1 (1.12) |
| run-406 | 3.0 (1.55) | 2.9 (1.19) | 2.9 (1.24) | 2.9 (1.02) | 2.8 (0.86) |
| run-407 | 4.9 (1.59) | 4.8 (1.27) | 4.8 (1.32) | 4.8 (1.12) | 4.8 (1.04) |
| run-408 | 4.2 (1.91) | 4.1 (1.50) | 4.1 (1.56) | 4.1 (1.27) | 4.1 (1.05) |
