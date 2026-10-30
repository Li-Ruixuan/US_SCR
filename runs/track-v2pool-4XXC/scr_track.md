# Single-model tracking: SCR alone on every 2th row (test_4XXC, `runs/v2pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **4.03** | 8.62 | 100 % | 1.083 | 1.33 |
| smoothed 0.25 s | **4.00** | 8.59 | 100 % | 0.463 | 1.01 |
| smoothed 0.5 s | **4.01** | 8.57 | 100 % | 0.470 | 1.05 |
| smoothed 1 s | **3.99** | 8.63 | 100 % | 0.304 | 0.84 |
| smoothed 2 s | **3.98** | 8.54 | 100 % | 0.291 | 0.79 |
| real time 0.25 s, delay 0 s | **3.94** | 8.58 | 100 % | 0.427 | 0.95 |
| real time 0.5 s, delay 0 s | **4.01** | 8.61 | 100 % | 0.571 | 1.17 |
| real time 1 s, delay 0 s | **4.05** | 8.68 | 100 % | 0.399 | 1.01 |
| real time 2 s, delay 0 s | **4.14** | 8.73 | 100 % | 0.348 | 1.01 |
| real time 0.25 s, delay 0.25 s | **4.13** | 8.61 | 100 % | 0.484 | 1.09 |
| real time 0.5 s, delay 0.25 s | **3.97** | 8.54 | 100 % | 0.304 | 0.76 |
| real time 1 s, delay 0.25 s | **3.98** | 8.53 | 100 % | 0.310 | 0.78 |
| real time 2 s, delay 0.25 s | **4.02** | 8.44 | 100 % | 0.300 | 0.80 |
| real time 0.25 s, delay 0.5 s | **4.97** | 9.60 | 100 % | 0.760 | 1.62 |
| real time 0.5 s, delay 0.5 s | **4.02** | 8.69 | 100 % | 0.607 | 1.26 |
| real time 1 s, delay 0.5 s | **3.95** | 8.45 | 100 % | 0.292 | 0.81 |
| real time 2 s, delay 0.5 s | **3.95** | 8.45 | 100 % | 0.301 | 0.85 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0.5 s | real time 0.5 s, delay 0.5 s | real time 1 s, delay 0.5 s | real time 2 s, delay 0.5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-413 | 3.0 (1.22) | 3.0 (0.89) | 3.0 (0.93) | 3.0 (0.71) | 3.0 (0.64) | 2.8 (0.83) | 3.0 (1.06) | 3.0 (0.88) | 3.1 (0.88) | 3.2 (0.97) | 3.0 (0.63) | 3.0 (0.65) | 3.0 (0.66) | 4.2 (1.48) | 3.0 (1.14) | 2.9 (0.67) | 2.9 (0.74) |
| run-414 | 4.4 (1.21) | 4.4 (0.93) | 4.4 (0.97) | 4.4 (0.80) | 4.4 (0.78) | 4.4 (0.89) | 4.4 (1.08) | 4.4 (0.95) | 4.5 (0.92) | 4.4 (1.00) | 4.3 (0.75) | 4.4 (0.76) | 4.4 (0.76) | 4.8 (1.51) | 4.4 (1.15) | 4.4 (0.81) | 4.3 (0.84) |
| run-415 | 4.5 (1.40) | 4.5 (1.01) | 4.5 (1.06) | 4.5 (0.81) | 4.5 (0.74) | 4.5 (0.94) | 4.5 (1.17) | 4.6 (0.97) | 4.6 (0.94) | 4.7 (1.07) | 4.5 (0.73) | 4.5 (0.76) | 4.6 (0.77) | 5.4 (1.49) | 4.5 (1.26) | 4.5 (0.76) | 4.5 (0.77) |
| run-416 | 4.2 (1.51) | 4.1 (1.19) | 4.2 (1.24) | 4.1 (1.03) | 4.1 (0.99) | 4.0 (1.13) | 4.2 (1.38) | 4.2 (1.26) | 4.4 (1.30) | 4.3 (1.29) | 4.0 (0.95) | 4.1 (0.97) | 4.2 (1.01) | 5.4 (1.98) | 4.2 (1.47) | 4.1 (0.99) | 4.1 (1.06) |
