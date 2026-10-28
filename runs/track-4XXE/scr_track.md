# Single-model tracking: SCR alone on every 2th row (test_4XXE, `runs/v2-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **6.12** | 10.52 | 94 % | 1.665 | 2.19 |
| smoothed 0.25 s | **6.28** | 12.27 | 100 % | 1.015 | 2.04 |
| smoothed 0.5 s | **6.29** | 12.27 | 100 % | 1.025 | 2.11 |
| smoothed 1 s | **6.29** | 12.25 | 100 % | 0.751 | 1.74 |
| smoothed 2 s | **6.25** | 11.93 | 100 % | 0.727 | 1.68 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-425 | 7.1 (2.47) | 7.0 (1.99) | 7.0 (2.09) | 7.1 (1.73) | 6.9 (1.65) |
| run-426 | 7.2 (2.27) | 7.2 (1.92) | 7.2 (2.01) | 7.3 (1.55) | 7.3 (1.50) |
| run-427 | 7.3 (2.27) | 8.1 (2.92) | 8.1 (2.95) | 8.1 (2.66) | 8.1 (2.61) |
| run-428 | 2.9 (1.76) | 2.8 (1.31) | 2.8 (1.37) | 2.6 (1.04) | 2.6 (0.96) |
