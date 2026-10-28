# Single-model tracking: SCR alone on every 2th row (test_4XXD, `runs/v2-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **9.57** | 14.24 | 96 % | 1.521 | 1.92 |
| smoothed 0.25 s | **9.67** | 14.93 | 100 % | 0.894 | 1.72 |
| smoothed 0.5 s | **9.68** | 14.92 | 100 % | 0.896 | 1.79 |
| smoothed 1 s | **9.67** | 14.92 | 100 % | 0.637 | 1.46 |
| smoothed 2 s | **9.63** | 15.02 | 100 % | 0.598 | 1.34 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-418 | 7.6 (1.48) | 7.5 (1.13) | 7.5 (1.19) | 7.5 (0.90) | 7.4 (0.82) |
| run-419 | 7.7 (1.71) | 7.7 (1.36) | 7.7 (1.44) | 7.7 (1.13) | 7.7 (1.11) |
| run-420 | 12.3 (2.22) | 12.9 (2.79) | 12.9 (2.84) | 12.9 (2.50) | 12.8 (2.32) |
| run-421 | 8.9 (2.43) | 9.1 (2.35) | 9.1 (2.43) | 9.1 (2.12) | 9.1 (2.07) |
| run-423 | 11.9 (2.49) | 12.0 (1.82) | 12.0 (1.88) | 11.9 (1.45) | 11.9 (1.19) |
| run-424 | 9.0 (1.18) | 8.9 (0.87) | 8.9 (0.94) | 8.9 (0.67) | 8.9 (0.56) |
