# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2fz-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.37** | 9.13 | 100 % | 1.625 | 1.90 |
| smoothed 0.25 s | **5.28** | 8.99 | 100 % | 0.689 | 1.41 |
| smoothed 0.5 s | **5.30** | 9.04 | 100 % | 0.676 | 1.47 |
| smoothed 1 s | **5.25** | 8.91 | 100 % | 0.396 | 1.12 |
| smoothed 2 s | **5.24** | 8.98 | 100 % | 0.347 | 0.97 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 4.7 (2.04) | 4.7 (1.54) | 4.7 (1.61) | 4.6 (1.30) | 4.6 (1.40) |
| run-402 | 6.1 (1.56) | 6.1 (1.11) | 6.1 (1.16) | 6.1 (0.85) | 6.0 (0.81) |
| run-403 | 4.2 (1.54) | 4.1 (1.08) | 4.1 (1.12) | 4.1 (0.82) | 4.1 (0.63) |
| run-404 | 5.0 (2.20) | 4.9 (1.62) | 4.9 (1.67) | 4.9 (1.22) | 4.8 (0.93) |
| run-405 | 6.0 (2.22) | 5.9 (1.66) | 5.9 (1.73) | 5.8 (1.29) | 5.9 (1.10) |
| run-406 | 5.5 (1.58) | 5.4 (1.16) | 5.4 (1.20) | 5.3 (0.93) | 5.3 (0.80) |
| run-407 | 5.7 (1.99) | 5.6 (1.51) | 5.6 (1.57) | 5.5 (1.28) | 5.4 (1.16) |
| run-408 | 5.7 (2.11) | 5.7 (1.64) | 5.8 (1.68) | 5.7 (1.24) | 5.8 (0.97) |
