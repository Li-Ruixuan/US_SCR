# Single-model tracking: SCR alone on every 2th row (test_4XXE, `runs/v2pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.92** | 9.87 | 95 % | 1.570 | 2.08 |
| smoothed 0.25 s | **5.90** | 11.15 | 100 % | 0.848 | 1.81 |
| smoothed 0.5 s | **5.92** | 11.11 | 100 % | 0.862 | 1.88 |
| smoothed 1 s | **5.89** | 10.90 | 100 % | 0.630 | 1.58 |
| smoothed 2 s | **5.92** | 10.80 | 100 % | 0.622 | 1.56 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-425 | 6.6 (2.26) | 6.4 (1.83) | 6.5 (1.91) | 6.4 (1.63) | 6.4 (1.66) |
| run-426 | 6.6 (2.23) | 6.6 (1.74) | 6.6 (1.83) | 6.6 (1.44) | 6.6 (1.45) |
| run-427 | 8.1 (2.13) | 8.5 (2.42) | 8.5 (2.47) | 8.5 (2.22) | 8.6 (2.17) |
| run-428 | 2.3 (1.69) | 2.1 (1.25) | 2.1 (1.30) | 2.0 (1.03) | 2.1 (0.94) |
