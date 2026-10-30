# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.03** | 3.77 | 100 % | 1.345 | 1.67 |
| smoothed 0.25 s | **1.91** | 3.58 | 100 % | 0.584 | 1.25 |
| smoothed 0.5 s | **1.93** | 3.61 | 100 % | 0.589 | 1.32 |
| smoothed 1 s | **1.89** | 3.49 | 100 % | 0.380 | 1.04 |
| smoothed 2 s | **1.85** | 3.41 | 100 % | 0.355 | 0.93 |
| real time 0.25 s, delay 0 s | **1.95** | 3.63 | 100 % | 0.531 | 1.18 |
| real time 0.5 s, delay 0 s | **1.96** | 3.68 | 100 % | 0.715 | 1.48 |
| real time 1 s, delay 0 s | **1.96** | 3.74 | 100 % | 0.501 | 1.28 |
| real time 2 s, delay 0 s | **2.11** | 4.24 | 100 % | 0.436 | 1.28 |
| real time 0.25 s, delay 0.25 s | **2.26** | 4.03 | 100 % | 0.606 | 1.38 |
| real time 0.5 s, delay 0.25 s | **1.86** | 3.44 | 100 % | 0.368 | 0.92 |
| real time 1 s, delay 0.25 s | **1.86** | 3.40 | 100 % | 0.372 | 0.93 |
| real time 2 s, delay 0.25 s | **1.85** | 3.41 | 100 % | 0.358 | 0.94 |
| real time 0.25 s, delay 0.5 s | **4.57** | 7.96 | 100 % | 0.979 | 2.21 |
| real time 0.5 s, delay 0.5 s | **1.98** | 3.73 | 100 % | 0.772 | 1.60 |
| real time 1 s, delay 0.5 s | **1.88** | 3.55 | 100 % | 0.340 | 0.96 |
| real time 2 s, delay 0.5 s | **1.96** | 3.71 | 100 % | 0.367 | 1.05 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0.5 s | real time 0.5 s, delay 0.5 s | real time 1 s, delay 0.5 s | real time 2 s, delay 0.5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-313 | 1.8 (1.35) | 1.7 (0.99) | 1.8 (1.04) | 1.7 (0.79) | 1.7 (0.71) | 1.6 (0.95) | 1.8 (1.20) | 1.8 (1.07) | 1.9 (1.01) | 2.0 (1.05) | 1.7 (0.71) | 1.7 (0.72) | 1.7 (0.73) | 4.3 (1.61) | 1.8 (1.25) | 1.7 (0.72) | 1.7 (0.74) |
| run-314 | 2.3 (1.55) | 2.2 (1.09) | 2.2 (1.15) | 2.1 (0.87) | 2.1 (0.65) | 2.3 (1.03) | 2.2 (1.33) | 2.2 (1.04) | 2.4 (0.82) | 2.2 (1.12) | 2.1 (0.73) | 2.1 (0.70) | 2.1 (0.63) | 3.7 (1.61) | 2.2 (1.38) | 2.1 (0.64) | 2.1 (0.69) |
| run-315 | 2.2 (1.91) | 2.0 (1.47) | 2.1 (1.55) | 2.0 (1.27) | 2.0 (1.12) | 2.0 (1.33) | 2.1 (1.70) | 2.1 (1.49) | 2.1 (1.47) | 2.3 (1.69) | 2.0 (1.14) | 2.0 (1.16) | 2.0 (1.13) | 4.0 (2.68) | 2.2 (1.91) | 2.0 (1.15) | 2.1 (1.30) |
| run-316 | 1.6 (1.58) | 1.5 (1.20) | 1.5 (1.27) | 1.5 (0.98) | 1.4 (0.91) | 1.6 (1.17) | 1.5 (1.42) | 1.5 (1.29) | 1.7 (1.41) | 2.1 (1.33) | 1.4 (0.87) | 1.4 (0.89) | 1.4 (0.98) | 5.3 (2.29) | 1.5 (1.55) | 1.4 (1.00) | 1.4 (1.15) |
| run-317 | 2.3 (1.94) | 2.1 (1.50) | 2.1 (1.58) | 2.1 (1.28) | 2.1 (1.26) | 2.2 (1.40) | 2.2 (1.74) | 2.2 (1.53) | 2.4 (1.70) | 2.6 (1.70) | 2.1 (1.15) | 2.1 (1.19) | 2.0 (1.24) | 5.7 (2.88) | 2.2 (1.93) | 2.2 (1.28) | 2.4 (1.39) |
