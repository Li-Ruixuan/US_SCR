# Single-model tracking: SCR alone on every 2th row (test_4XXD, `runs/v2map-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **11.73** | 16.63 | 97 % | 1.367 | 1.76 |
| smoothed 0.25 s | **11.54** | 16.68 | 100 % | 0.665 | 1.47 |
| smoothed 0.5 s | **11.54** | 16.70 | 100 % | 0.669 | 1.53 |
| smoothed 1 s | **11.51** | 16.74 | 100 % | 0.430 | 1.23 |
| smoothed 2 s | **11.54** | 16.70 | 100 % | 0.391 | 1.12 |
| real time 0.25 s, delay 0.25 s | **11.67** | 16.89 | 100 % | 0.648 | 1.54 |
| real time 0.5 s, delay 0.25 s | **11.60** | 16.89 | 100 % | 0.416 | 1.11 |
| real time 1 s, delay 0.25 s | **11.61** | 16.92 | 100 % | 0.447 | 1.18 |
| real time 2 s, delay 0.25 s | **11.70** | 17.04 | 100 % | 0.455 | 1.28 |
| real time 0.25 s, delay 0 s | **11.66** | 16.82 | 100 % | 0.568 | 1.35 |
| real time 0.5 s, delay 0 s | **11.67** | 16.90 | 100 % | 0.751 | 1.66 |
| real time 1 s, delay 0 s | **11.69** | 17.03 | 100 % | 0.573 | 1.52 |
| real time 2 s, delay 0 s | **11.74** | 17.26 | 100 % | 0.521 | 1.58 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-418 | 11.9 (1.37) | 11.8 (1.05) | 11.8 (1.10) | 11.8 (0.86) | 11.8 (0.77) | 11.9 (1.13) | 11.9 (0.77) | 11.8 (0.79) | 11.9 (0.82) | 11.8 (0.98) | 11.8 (1.21) | 11.9 (1.04) | 11.9 (1.05) |
| run-419 | 12.0 (1.57) | 11.8 (1.25) | 11.8 (1.32) | 11.7 (1.02) | 11.7 (1.02) | 11.8 (1.42) | 11.7 (0.94) | 11.7 (1.00) | 11.8 (1.01) | 11.8 (1.11) | 11.8 (1.44) | 11.7 (1.20) | 11.8 (1.22) |
| run-420 | 15.6 (2.04) | 15.0 (1.83) | 15.0 (1.85) | 15.1 (1.54) | 15.1 (1.40) | 15.6 (1.89) | 15.6 (1.44) | 15.6 (1.53) | 15.9 (1.76) | 15.7 (1.72) | 15.7 (2.04) | 15.8 (1.91) | 16.0 (2.09) |
| run-421 | 12.3 (2.29) | 12.1 (1.92) | 12.1 (2.00) | 12.1 (1.64) | 12.2 (1.55) | 12.2 (2.00) | 12.1 (1.46) | 12.1 (1.64) | 12.2 (1.96) | 12.2 (1.82) | 12.3 (2.24) | 12.3 (2.20) | 12.3 (2.50) |
| run-423 | 8.1 (2.20) | 8.1 (1.98) | 8.1 (2.04) | 8.0 (1.68) | 8.1 (1.45) | 8.1 (1.91) | 8.1 (1.50) | 8.1 (1.54) | 8.1 (1.56) | 8.1 (1.73) | 8.1 (2.09) | 8.1 (2.00) | 8.1 (1.88) |
| run-424 | 10.5 (1.11) | 10.4 (0.80) | 10.4 (0.86) | 10.4 (0.62) | 10.4 (0.55) | 10.5 (0.86) | 10.4 (0.55) | 10.4 (0.57) | 10.4 (0.58) | 10.4 (0.74) | 10.4 (0.93) | 10.4 (0.76) | 10.3 (0.76) |
