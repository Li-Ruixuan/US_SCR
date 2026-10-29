# Single-model tracking: SCR alone on every 2th row (test_4XXD, `runs/v2pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **8.44** | 13.14 | 98 % | 1.876 | 2.23 |
| smoothed 0.25 s | **8.50** | 13.23 | 100 % | 0.806 | 1.69 |
| smoothed 0.5 s | **8.50** | 13.23 | 100 % | 0.837 | 1.80 |
| smoothed 1 s | **8.48** | 13.12 | 100 % | 0.475 | 1.37 |
| smoothed 2 s | **8.46** | 12.99 | 100 % | 0.405 | 1.17 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-418 | 6.8 (1.44) | 6.7 (1.09) | 6.7 (1.13) | 6.6 (0.89) | 6.7 (0.79) |
| run-419 | 6.8 (1.58) | 6.8 (1.26) | 6.8 (1.33) | 6.7 (1.03) | 6.6 (1.04) |
| run-420 | 12.4 (4.77) | 12.6 (3.22) | 12.7 (3.58) | 12.7 (2.40) | 12.7 (1.72) |
| run-421 | 9.3 (2.20) | 9.6 (2.01) | 9.6 (2.07) | 9.6 (1.82) | 9.6 (1.73) |
| run-423 | 8.7 (2.25) | 8.7 (1.70) | 8.7 (1.78) | 8.7 (1.39) | 8.7 (1.17) |
| run-424 | 6.6 (1.15) | 6.6 (0.87) | 6.6 (0.92) | 6.6 (0.68) | 6.5 (0.59) |
