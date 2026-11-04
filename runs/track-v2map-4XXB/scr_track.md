# Single-model tracking: SCR alone on every 2th row (test_4XXB, `runs/v2map-4XXB/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXB/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **6.57** | 8.18 | 100 % | 1.280 | 1.57 |
| smoothed 0.25 s | **6.54** | 7.98 | 100 % | 0.556 | 1.18 |
| smoothed 0.5 s | **6.53** | 7.97 | 100 % | 0.553 | 1.23 |
| smoothed 1 s | **6.54** | 7.94 | 100 % | 0.353 | 0.98 |
| smoothed 2 s | **6.55** | 7.89 | 100 % | 0.321 | 0.87 |
| real time 0.25 s, delay 0.25 s | **6.60** | 8.14 | 100 % | 0.577 | 1.29 |
| real time 0.5 s, delay 0.25 s | **6.54** | 7.91 | 100 % | 0.349 | 0.87 |
| real time 1 s, delay 0.25 s | **6.54** | 7.90 | 100 % | 0.354 | 0.89 |
| real time 2 s, delay 0.25 s | **6.53** | 7.91 | 100 % | 0.336 | 0.88 |
| real time 0.25 s, delay 0 s | **6.50** | 7.99 | 100 % | 0.490 | 1.07 |
| real time 0.5 s, delay 0 s | **6.53** | 8.06 | 100 % | 0.665 | 1.36 |
| real time 1 s, delay 0 s | **6.55** | 8.03 | 100 % | 0.453 | 1.15 |
| real time 2 s, delay 0 s | **6.60** | 8.25 | 100 % | 0.388 | 1.12 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-409 | 6.9 (1.44) | 6.9 (1.04) | 6.9 (1.09) | 6.9 (0.87) | 6.9 (0.93) | 7.0 (1.27) | 6.9 (0.81) | 6.9 (0.90) | 6.9 (0.92) | 6.8 (0.89) | 6.9 (1.18) | 6.9 (0.99) | 6.9 (1.09) |
| run-410 | 5.9 (1.39) | 5.9 (1.02) | 5.9 (1.07) | 5.9 (0.83) | 5.9 (0.73) | 6.0 (1.12) | 5.9 (0.74) | 5.9 (0.76) | 5.9 (0.74) | 5.9 (0.92) | 5.9 (1.18) | 5.9 (0.93) | 5.9 (0.90) |
| run-411 | 5.8 (1.88) | 5.8 (1.44) | 5.8 (1.51) | 5.8 (1.20) | 5.9 (0.95) | 5.8 (1.51) | 5.9 (1.03) | 5.9 (1.01) | 5.9 (0.98) | 5.9 (1.36) | 5.8 (1.73) | 5.9 (1.47) | 5.9 (1.35) |
| run-412 | 7.6 (1.56) | 7.5 (1.20) | 7.5 (1.23) | 7.5 (1.00) | 7.5 (0.88) | 7.6 (1.27) | 7.5 (0.89) | 7.5 (0.90) | 7.5 (0.89) | 7.4 (1.11) | 7.5 (1.37) | 7.5 (1.20) | 7.6 (1.14) |
