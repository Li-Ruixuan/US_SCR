# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2-5XXA-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.02** | 3.89 | 100 % | 1.243 | 1.48 |
| smoothed 0.25 s | **1.90** | 3.68 | 100 % | 0.504 | 1.06 |
| smoothed 0.5 s | **1.92** | 3.68 | 100 % | 0.510 | 1.12 |
| smoothed 1 s | **1.85** | 3.61 | 100 % | 0.283 | 0.82 |
| smoothed 2 s | **1.81** | 3.52 | 100 % | 0.221 | 0.62 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.6 (1.40) | 2.5 (1.00) | 2.5 (1.06) | 2.5 (0.78) | 2.4 (0.54) |
| run-502 | 2.0 (1.24) | 1.9 (0.91) | 1.9 (0.96) | 1.9 (0.71) | 1.8 (0.60) |
| run-503 | 2.4 (1.36) | 2.3 (0.98) | 2.3 (1.03) | 2.3 (0.77) | 2.3 (0.60) |
| run-504 | 2.0 (1.89) | 1.9 (1.37) | 1.9 (1.44) | 1.8 (1.11) | 1.8 (0.85) |
| run-505 | 2.4 (1.79) | 2.3 (1.34) | 2.3 (1.42) | 2.2 (1.07) | 2.2 (0.83) |
| run-506 | 2.0 (1.46) | 1.9 (1.05) | 1.9 (1.11) | 1.9 (0.81) | 1.7 (0.58) |
| run-507 | 1.5 (1.42) | 1.3 (0.93) | 1.3 (0.99) | 1.3 (0.67) | 1.3 (0.46) |
| run-508 | 1.3 (1.26) | 1.1 (0.90) | 1.1 (0.95) | 1.0 (0.66) | 0.9 (0.47) |
