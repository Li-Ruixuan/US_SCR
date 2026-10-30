# Single-model tracking: SCR alone on every 2th row (test_4XXB, `runs/v2pool-4XXB/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.80** | 6.59 | 100 % | 1.201 | 1.47 |
| smoothed 0.25 s | **3.76** | 6.42 | 100 % | 0.529 | 1.11 |
| smoothed 0.5 s | **3.76** | 6.43 | 100 % | 0.529 | 1.16 |
| smoothed 1 s | **3.74** | 6.44 | 100 % | 0.336 | 0.90 |
| smoothed 2 s | **3.76** | 6.40 | 100 % | 0.313 | 0.83 |
| real time 0.25 s, delay 0 s | **3.67** | 6.65 | 100 % | 0.468 | 1.02 |
| real time 0.5 s, delay 0 s | **3.77** | 6.52 | 100 % | 0.632 | 1.29 |
| real time 1 s, delay 0 s | **3.76** | 6.61 | 100 % | 0.434 | 1.08 |
| real time 2 s, delay 0 s | **3.88** | 6.91 | 100 % | 0.380 | 1.09 |
| real time 0.25 s, delay 0.25 s | **3.94** | 6.60 | 100 % | 0.551 | 1.21 |
| real time 0.5 s, delay 0.25 s | **3.73** | 6.38 | 100 % | 0.332 | 0.81 |
| real time 1 s, delay 0.25 s | **3.75** | 6.37 | 100 % | 0.338 | 0.84 |
| real time 2 s, delay 0.25 s | **3.77** | 6.54 | 100 % | 0.324 | 0.85 |
| real time 0.25 s, delay 0.5 s | **4.83** | 9.32 | 100 % | 0.869 | 1.87 |
| real time 0.5 s, delay 0.5 s | **3.78** | 6.55 | 100 % | 0.691 | 1.42 |
| real time 1 s, delay 0.5 s | **3.74** | 6.43 | 100 % | 0.317 | 0.87 |
| real time 2 s, delay 0.5 s | **3.74** | 6.46 | 100 % | 0.327 | 0.91 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0.5 s | real time 0.5 s, delay 0.5 s | real time 1 s, delay 0.5 s | real time 2 s, delay 0.5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-409 | 4.6 (1.33) | 4.5 (0.98) | 4.5 (1.03) | 4.5 (0.82) | 4.6 (0.89) | 4.4 (0.84) | 4.5 (1.10) | 4.5 (0.96) | 4.6 (1.08) | 4.7 (1.20) | 4.5 (0.77) | 4.5 (0.86) | 4.5 (0.89) | 5.1 (2.02) | 4.6 (1.38) | 4.5 (0.96) | 4.6 (1.01) |
| run-410 | 3.3 (1.31) | 3.3 (0.99) | 3.3 (1.04) | 3.3 (0.82) | 3.3 (0.76) | 3.3 (0.90) | 3.3 (1.13) | 3.3 (0.93) | 3.3 (0.93) | 3.4 (1.09) | 3.3 (0.75) | 3.3 (0.78) | 3.3 (0.76) | 4.1 (1.68) | 3.3 (1.25) | 3.3 (0.79) | 3.3 (0.85) |
| run-411 | 3.1 (1.72) | 3.1 (1.31) | 3.1 (1.37) | 3.2 (1.07) | 3.1 (0.88) | 3.0 (1.23) | 3.1 (1.57) | 3.1 (1.30) | 3.2 (1.27) | 3.3 (1.37) | 3.1 (0.93) | 3.1 (0.91) | 3.1 (0.90) | 4.4 (1.97) | 3.1 (1.63) | 3.1 (0.88) | 3.1 (0.92) |
| run-412 | 4.2 (1.51) | 4.1 (1.14) | 4.2 (1.19) | 4.0 (0.91) | 4.1 (0.81) | 4.0 (1.08) | 4.2 (1.36) | 4.2 (1.15) | 4.4 (1.09) | 4.3 (1.19) | 4.0 (0.80) | 4.0 (0.81) | 4.2 (0.83) | 5.7 (1.81) | 4.2 (1.41) | 4.0 (0.84) | 4.1 (0.87) |
