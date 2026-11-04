# Single-model tracking: SCR alone on every 2th row (test_4XXC, `runs/v2map-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **9.44** | 13.19 | 100 % | 1.080 | 1.31 |
| smoothed 0.25 s | **9.42** | 13.16 | 100 % | 0.454 | 0.96 |
| smoothed 0.5 s | **9.42** | 13.17 | 100 % | 0.460 | 1.01 |
| smoothed 1 s | **9.43** | 13.17 | 100 % | 0.295 | 0.78 |
| smoothed 2 s | **9.40** | 13.15 | 100 % | 0.281 | 0.74 |
| real time 0.25 s, delay 0.25 s | **9.46** | 13.18 | 100 % | 0.475 | 1.04 |
| real time 0.5 s, delay 0.25 s | **9.41** | 13.15 | 100 % | 0.295 | 0.71 |
| real time 1 s, delay 0.25 s | **9.41** | 13.13 | 100 % | 0.301 | 0.73 |
| real time 2 s, delay 0.25 s | **9.40** | 13.10 | 100 % | 0.290 | 0.75 |
| real time 0.25 s, delay 0 s | **9.42** | 13.14 | 100 % | 0.418 | 0.90 |
| real time 0.5 s, delay 0 s | **9.45** | 13.19 | 100 % | 0.568 | 1.14 |
| real time 1 s, delay 0 s | **9.44** | 13.17 | 100 % | 0.387 | 0.96 |
| real time 2 s, delay 0 s | **9.48** | 13.23 | 100 % | 0.338 | 0.96 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-413 | 8.0 (1.23) | 8.0 (0.90) | 8.0 (0.94) | 8.0 (0.73) | 7.9 (0.66) | 8.0 (0.99) | 7.9 (0.64) | 7.9 (0.66) | 7.9 (0.66) | 8.0 (0.83) | 8.1 (1.09) | 8.1 (0.90) | 8.1 (0.88) |
| run-414 | 11.6 (1.27) | 11.7 (0.94) | 11.7 (0.98) | 11.7 (0.79) | 11.7 (0.74) | 11.7 (1.02) | 11.7 (0.73) | 11.7 (0.74) | 11.7 (0.73) | 11.7 (0.89) | 11.7 (1.10) | 11.7 (0.94) | 11.8 (0.91) |
| run-415 | 9.2 (1.38) | 9.1 (1.01) | 9.1 (1.07) | 9.1 (0.80) | 9.2 (0.74) | 9.2 (1.07) | 9.2 (0.72) | 9.2 (0.75) | 9.1 (0.74) | 9.1 (0.95) | 9.2 (1.19) | 9.1 (0.95) | 9.1 (0.91) |
| run-416 | 8.9 (1.34) | 8.9 (0.98) | 8.9 (1.03) | 8.9 (0.82) | 8.9 (0.81) | 8.9 (1.09) | 8.9 (0.75) | 8.9 (0.78) | 8.9 (0.86) | 8.9 (0.95) | 8.9 (1.17) | 8.9 (1.03) | 8.9 (1.14) |
