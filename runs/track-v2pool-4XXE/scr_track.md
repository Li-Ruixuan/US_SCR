# Single-model tracking: SCR alone on every 2th row (test_4XXE, `runs/v2pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.92** | 9.87 | 95 % | 1.570 | 2.08 |
| smoothed 0.25 s | **5.90** | 11.15 | 100 % | 0.848 | 1.81 |
| smoothed 0.5 s | **5.92** | 11.11 | 100 % | 0.862 | 1.88 |
| smoothed 1 s | **5.89** | 10.90 | 100 % | 0.630 | 1.58 |
| smoothed 2 s | **5.92** | 10.80 | 100 % | 0.622 | 1.56 |
| real time 0.25 s, delay 0 s | **6.08** | 11.03 | 100 % | 0.652 | 1.58 |
| real time 0.5 s, delay 0 s | **6.03** | 11.23 | 100 % | 0.856 | 1.92 |
| real time 1 s, delay 0 s | **6.09** | 11.27 | 100 % | 0.658 | 1.81 |
| real time 2 s, delay 0 s | **6.47** | 11.71 | 100 % | 0.676 | 2.09 |
| real time 0.25 s, delay 0.25 s | **6.00** | 11.13 | 100 % | 0.758 | 1.84 |
| real time 0.5 s, delay 0.25 s | **5.87** | 10.92 | 100 % | 0.497 | 1.34 |
| real time 1 s, delay 0.25 s | **5.88** | 10.92 | 100 % | 0.533 | 1.44 |
| real time 2 s, delay 0.25 s | **5.95** | 11.37 | 100 % | 0.576 | 1.63 |
| real time 0.25 s, delay 0.5 s | **7.26** | 13.02 | 100 % | 1.163 | 2.79 |
| real time 0.5 s, delay 0.5 s | **6.03** | 11.10 | 100 % | 0.944 | 2.12 |
| real time 1 s, delay 0.5 s | **5.85** | 10.90 | 100 % | 0.520 | 1.50 |
| real time 2 s, delay 0.5 s | **5.86** | 11.22 | 100 % | 0.586 | 1.72 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0.5 s | real time 0.5 s, delay 0.5 s | real time 1 s, delay 0.5 s | real time 2 s, delay 0.5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-425 | 6.6 (2.26) | 6.4 (1.83) | 6.5 (1.91) | 6.4 (1.63) | 6.4 (1.66) | 6.5 (1.73) | 6.5 (2.10) | 6.7 (2.02) | 7.5 (2.40) | 6.6 (2.13) | 6.4 (1.54) | 6.4 (1.61) | 6.4 (1.77) | 8.3 (3.60) | 6.6 (2.36) | 6.3 (1.79) | 6.4 (1.95) |
| run-426 | 6.6 (2.23) | 6.6 (1.74) | 6.6 (1.83) | 6.6 (1.44) | 6.6 (1.45) | 6.9 (1.63) | 6.7 (1.99) | 6.7 (1.71) | 7.1 (1.86) | 6.6 (1.92) | 6.6 (1.33) | 6.6 (1.41) | 6.7 (1.47) | 7.9 (2.95) | 6.6 (2.23) | 6.4 (1.52) | 6.5 (1.59) |
| run-427 | 8.1 (2.13) | 8.5 (2.42) | 8.5 (2.47) | 8.5 (2.22) | 8.6 (2.17) | 8.7 (1.84) | 8.7 (2.16) | 8.7 (2.31) | 8.8 (2.92) | 8.6 (1.94) | 8.5 (1.58) | 8.5 (1.76) | 8.5 (2.33) | 9.3 (2.54) | 8.6 (2.26) | 8.6 (1.70) | 8.4 (2.28) |
| run-428 | 2.3 (1.69) | 2.1 (1.25) | 2.1 (1.30) | 2.0 (1.03) | 2.1 (0.94) | 2.2 (1.14) | 2.2 (1.43) | 2.2 (1.20) | 2.5 (1.19) | 2.2 (1.38) | 2.0 (0.93) | 2.1 (0.97) | 2.3 (0.97) | 3.5 (2.07) | 2.3 (1.62) | 2.1 (0.98) | 2.2 (1.05) |
