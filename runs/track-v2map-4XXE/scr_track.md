# Single-model tracking: SCR alone on every 2th row (test_4XXE, `runs/v2map-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **7.16** | 10.85 | 95 % | 1.492 | 1.99 |
| smoothed 0.25 s | **7.05** | 10.74 | 100 % | 0.759 | 1.67 |
| smoothed 0.5 s | **7.06** | 10.77 | 100 % | 0.777 | 1.74 |
| smoothed 1 s | **7.06** | 10.66 | 100 % | 0.543 | 1.42 |
| smoothed 2 s | **7.07** | 10.69 | 100 % | 0.752 | 1.64 |
| real time 0.25 s, delay 0.25 s | **7.20** | 10.91 | 100 % | 0.751 | 1.79 |
| real time 0.5 s, delay 0.25 s | **7.05** | 10.65 | 100 % | 0.479 | 1.26 |
| real time 1 s, delay 0.25 s | **7.05** | 10.63 | 100 % | 0.516 | 1.36 |
| real time 2 s, delay 0.25 s | **7.10** | 10.82 | 100 % | 0.561 | 1.57 |
| real time 0.25 s, delay 0 s | **7.05** | 10.71 | 100 % | 0.616 | 1.48 |
| real time 0.5 s, delay 0 s | **7.06** | 10.79 | 100 % | 0.816 | 1.84 |
| real time 1 s, delay 0 s | **7.11** | 10.84 | 100 % | 0.625 | 1.69 |
| real time 2 s, delay 0 s | **7.28** | 11.60 | 100 % | 0.666 | 2.03 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-425 | 5.4 (2.22) | 5.3 (1.80) | 5.3 (1.89) | 5.3 (1.59) | 5.3 (1.59) | 5.5 (2.14) | 5.3 (1.48) | 5.2 (1.53) | 5.3 (1.69) | 5.3 (1.62) | 5.3 (2.03) | 5.4 (1.85) | 5.7 (2.24) |
| run-426 | 6.9 (2.12) | 7.0 (1.67) | 7.0 (1.75) | 6.9 (1.38) | 7.0 (1.43) | 7.1 (1.87) | 7.0 (1.30) | 7.0 (1.39) | 7.1 (1.46) | 7.0 (1.54) | 6.9 (1.92) | 6.9 (1.64) | 7.2 (1.84) |
| run-427 | 11.8 (1.97) | 11.6 (1.97) | 11.6 (2.02) | 11.6 (1.75) | 11.7 (2.62) | 11.6 (1.79) | 11.6 (1.40) | 11.6 (1.59) | 11.7 (2.20) | 11.6 (1.65) | 11.6 (1.99) | 11.8 (2.16) | 11.8 (2.93) |
| run-428 | 4.5 (1.64) | 4.4 (1.23) | 4.4 (1.30) | 4.4 (0.98) | 4.4 (0.91) | 4.6 (1.38) | 4.3 (0.88) | 4.4 (0.93) | 4.3 (0.93) | 4.3 (1.09) | 4.4 (1.40) | 4.4 (1.11) | 4.4 (1.12) |
