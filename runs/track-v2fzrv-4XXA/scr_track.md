# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2fzrv-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.65** | 9.28 | 100 % | 1.675 | 1.95 |
| smoothed 0.25 s | **5.55** | 9.19 | 100 % | 0.708 | 1.43 |
| smoothed 0.5 s | **5.55** | 9.18 | 100 % | 0.694 | 1.49 |
| smoothed 1 s | **5.50** | 9.13 | 100 % | 0.399 | 1.12 |
| smoothed 2 s | **5.51** | 9.07 | 100 % | 0.343 | 0.95 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 5.0 (2.10) | 4.9 (1.59) | 4.9 (1.66) | 4.9 (1.35) | 4.8 (1.43) |
| run-402 | 6.4 (1.62) | 6.3 (1.14) | 6.4 (1.19) | 6.3 (0.87) | 6.4 (0.80) |
| run-403 | 4.3 (1.57) | 4.2 (1.12) | 4.2 (1.17) | 4.2 (0.84) | 4.2 (0.62) |
| run-404 | 5.1 (2.34) | 5.0 (1.72) | 5.0 (1.79) | 5.0 (1.26) | 4.9 (0.95) |
| run-405 | 5.7 (2.27) | 5.5 (1.74) | 5.5 (1.80) | 5.4 (1.33) | 5.4 (1.08) |
| run-406 | 6.1 (1.61) | 6.1 (1.17) | 6.1 (1.23) | 6.0 (0.94) | 6.0 (0.79) |
| run-407 | 6.3 (1.97) | 6.0 (1.46) | 6.0 (1.48) | 6.0 (1.21) | 6.0 (1.06) |
| run-408 | 6.3 (2.10) | 6.3 (1.54) | 6.3 (1.60) | 6.3 (1.19) | 6.4 (0.92) |
