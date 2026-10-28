# Single-model tracking: SCR alone on every 2th row (test_4XXB, `runs/v2-4XXB/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.82** | 7.76 | 100 % | 1.443 | 1.76 |
| smoothed 0.25 s | **5.80** | 7.63 | 100 % | 0.614 | 1.32 |
| smoothed 0.5 s | **5.82** | 7.64 | 100 % | 0.611 | 1.37 |
| smoothed 1 s | **5.79** | 7.56 | 100 % | 0.378 | 1.07 |
| smoothed 2 s | **5.77** | 7.48 | 100 % | 0.332 | 0.92 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-409 | 6.8 (1.49) | 6.8 (1.08) | 6.8 (1.13) | 6.8 (0.90) | 6.8 (0.92) |
| run-410 | 5.4 (1.49) | 5.4 (1.11) | 5.4 (1.16) | 5.4 (0.91) | 5.3 (0.77) |
| run-411 | 4.2 (1.99) | 4.2 (1.54) | 4.2 (1.62) | 4.2 (1.26) | 4.2 (1.06) |
| run-412 | 6.8 (2.08) | 6.8 (1.54) | 6.8 (1.58) | 6.8 (1.22) | 6.8 (0.93) |
