# Single-model tracking: SCR alone on every 2th row (test_4XXB, `runs/v2pool-4XXB/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.80** | 6.59 | 100 % | 1.201 | 1.47 |
| smoothed 0.25 s | **3.76** | 6.42 | 100 % | 0.529 | 1.11 |
| smoothed 0.5 s | **3.76** | 6.43 | 100 % | 0.529 | 1.16 |
| smoothed 1 s | **3.74** | 6.44 | 100 % | 0.336 | 0.90 |
| smoothed 2 s | **3.76** | 6.40 | 100 % | 0.313 | 0.83 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-409 | 4.6 (1.33) | 4.5 (0.98) | 4.5 (1.03) | 4.5 (0.82) | 4.6 (0.89) |
| run-410 | 3.3 (1.31) | 3.3 (0.99) | 3.3 (1.04) | 3.3 (0.82) | 3.3 (0.76) |
| run-411 | 3.1 (1.72) | 3.1 (1.31) | 3.1 (1.37) | 3.2 (1.07) | 3.1 (0.88) |
| run-412 | 4.2 (1.51) | 4.1 (1.14) | 4.2 (1.19) | 4.0 (0.91) | 4.1 (0.81) |
