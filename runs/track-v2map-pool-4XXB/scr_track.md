# Single-model tracking: SCR alone on every 2th row (test_4XXB, `runs/v2map-pool-4XXB/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-pool-4XXB/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **8.12** | 10.84 | 100 % | 1.291 | 1.54 |
| smoothed 0.25 s | **8.09** | 10.75 | 100 % | 0.539 | 1.17 |
| smoothed 0.5 s | **8.10** | 10.76 | 100 % | 0.535 | 1.22 |
| smoothed 1 s | **8.08** | 10.76 | 100 % | 0.359 | 0.99 |
| smoothed 2 s | **8.08** | 10.87 | 100 % | 0.330 | 0.90 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-409 | 9.2 (1.29) | 9.2 (0.93) | 9.2 (0.98) | 9.1 (0.78) | 9.2 (0.87) |
| run-410 | 7.4 (1.25) | 7.4 (0.95) | 7.4 (0.99) | 7.4 (0.78) | 7.4 (0.71) |
| run-411 | 7.8 (2.20) | 7.8 (1.74) | 7.7 (1.80) | 7.7 (1.51) | 7.7 (1.22) |
| run-412 | 8.1 (1.40) | 8.1 (1.06) | 8.1 (1.09) | 8.1 (0.87) | 8.1 (0.79) |
