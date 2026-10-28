# Single-model tracking: SCR alone on every 2th row (test_4XXC, `runs/v2-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.76** | 10.90 | 100 % | 1.186 | 1.48 |
| smoothed 0.25 s | **5.67** | 10.87 | 100 % | 0.504 | 1.11 |
| smoothed 0.5 s | **5.69** | 10.80 | 100 % | 0.512 | 1.16 |
| smoothed 1 s | **5.66** | 10.82 | 100 % | 0.325 | 0.91 |
| smoothed 2 s | **5.63** | 10.76 | 100 % | 0.298 | 0.82 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-413 | 4.5 (1.27) | 4.3 (0.93) | 4.3 (0.97) | 4.2 (0.75) | 4.1 (0.66) |
| run-414 | 7.9 (1.46) | 7.9 (1.10) | 7.9 (1.15) | 7.9 (0.93) | 7.9 (0.85) |
| run-415 | 5.0 (1.51) | 5.0 (1.12) | 5.0 (1.19) | 5.0 (0.90) | 5.0 (0.79) |
| run-416 | 5.6 (1.68) | 5.6 (1.28) | 5.6 (1.33) | 5.5 (1.08) | 5.5 (1.00) |
