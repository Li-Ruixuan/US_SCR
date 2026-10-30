# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2-3XX-room301/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.12** | 5.64 | 100 % | 1.474 | 1.94 |
| smoothed 0.25 s | **2.97** | 5.45 | 100 % | 0.669 | 1.52 |
| smoothed 0.5 s | **2.98** | 5.48 | 100 % | 0.675 | 1.59 |
| smoothed 1 s | **2.92** | 5.34 | 100 % | 0.462 | 1.30 |
| smoothed 2 s | **2.98** | 5.34 | 100 % | 0.442 | 1.18 |
| real time 0.25 s, delay 0 s | **3.05** | 5.46 | 100 % | 0.595 | 1.42 |
| real time 0.5 s, delay 0 s | **3.04** | 5.55 | 100 % | 0.800 | 1.76 |
| real time 1 s, delay 0 s | **3.09** | 5.55 | 100 % | 0.577 | 1.54 |
| real time 2 s, delay 0 s | **3.16** | 6.05 | 100 % | 0.516 | 1.56 |
| real time 0.25 s, delay 0.25 s | **3.31** | 5.75 | 100 % | 0.706 | 1.69 |
| real time 0.5 s, delay 0.25 s | **2.92** | 5.24 | 100 % | 0.437 | 1.15 |
| real time 1 s, delay 0.25 s | **2.95** | 5.24 | 100 % | 0.443 | 1.17 |
| real time 2 s, delay 0.25 s | **2.95** | 5.27 | 100 % | 0.430 | 1.18 |
| real time 0.25 s, delay 0.5 s | **5.74** | 9.38 | 100 % | 1.123 | 2.70 |
| real time 0.5 s, delay 0.5 s | **3.06** | 5.63 | 100 % | 0.891 | 1.94 |
| real time 1 s, delay 0.5 s | **3.00** | 5.49 | 100 % | 0.414 | 1.21 |
| real time 2 s, delay 0.5 s | **3.06** | 5.54 | 100 % | 0.455 | 1.35 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0.5 s | real time 0.5 s, delay 0.5 s | real time 1 s, delay 0.5 s | real time 2 s, delay 0.5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-315 | 3.8 (2.06) | 3.6 (1.65) | 3.6 (1.72) | 3.6 (1.43) | 3.7 (1.23) | 3.7 (1.52) | 3.7 (1.90) | 3.7 (1.71) | 3.9 (1.55) | 3.8 (1.84) | 3.6 (1.26) | 3.6 (1.27) | 3.7 (1.20) | 5.3 (2.77) | 3.7 (2.11) | 3.7 (1.23) | 3.8 (1.38) |
| run-316 | 2.5 (1.64) | 2.4 (1.24) | 2.4 (1.31) | 2.3 (1.02) | 2.4 (0.94) | 2.6 (1.18) | 2.5 (1.43) | 2.6 (1.26) | 2.7 (1.40) | 2.9 (1.36) | 2.3 (0.91) | 2.3 (0.93) | 2.4 (1.02) | 5.7 (2.32) | 2.4 (1.58) | 2.3 (1.03) | 2.4 (1.20) |
| run-317 | 3.0 (2.13) | 3.0 (1.67) | 3.0 (1.75) | 2.9 (1.44) | 2.9 (1.35) | 2.8 (1.54) | 3.0 (1.93) | 3.0 (1.65) | 2.9 (1.72) | 3.2 (1.87) | 2.9 (1.28) | 2.9 (1.31) | 2.7 (1.31) | 6.3 (3.01) | 3.1 (2.12) | 3.0 (1.37) | 3.1 (1.47) |
