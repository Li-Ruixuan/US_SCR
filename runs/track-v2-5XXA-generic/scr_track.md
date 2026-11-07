# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2-5XXA-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **11.06** | 18.19 | 100 % | 1.889 | 2.23 |
| smoothed 0.25 s | **10.98** | 18.07 | 100 % | 0.751 | 1.63 |
| smoothed 0.5 s | **10.98** | 18.07 | 100 % | 0.763 | 1.72 |
| smoothed 1 s | **10.95** | 18.10 | 100 % | 0.407 | 1.30 |
| smoothed 2 s | **10.93** | 18.12 | 100 % | 0.301 | 0.97 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 11.5 (1.73) | 11.5 (1.22) | 11.4 (1.29) | 11.5 (0.96) | 11.5 (0.73) |
| run-502 | 13.0 (1.68) | 13.0 (1.22) | 12.9 (1.29) | 13.0 (1.00) | 13.0 (0.82) |
| run-503 | 14.1 (3.17) | 13.9 (2.26) | 14.0 (2.45) | 13.8 (1.74) | 13.8 (1.20) |
| run-504 | 8.1 (2.74) | 7.9 (2.03) | 7.9 (2.12) | 7.9 (1.67) | 7.9 (1.34) |
| run-505 | 8.5 (2.93) | 8.4 (2.39) | 8.4 (2.48) | 8.4 (1.98) | 8.4 (1.52) |
| run-506 | 8.8 (1.90) | 8.7 (1.37) | 8.7 (1.43) | 8.7 (1.08) | 8.6 (0.83) |
| run-507 | 13.7 (2.09) | 13.6 (1.40) | 13.6 (1.50) | 13.4 (1.06) | 13.3 (0.72) |
| run-508 | 10.8 (1.59) | 10.9 (1.14) | 10.9 (1.20) | 10.8 (0.87) | 10.8 (0.61) |
