# Single-model tracking: SCR alone on every 2th row (test_4XXC, `runs/v2map-4XXC-owncalib/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXC-owncalib/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **7.92** | 11.48 | 100 % | 1.068 | 1.29 |
| smoothed 0.25 s | **7.88** | 11.46 | 100 % | 0.448 | 0.95 |
| smoothed 0.5 s | **7.89** | 11.43 | 100 % | 0.454 | 1.00 |
| smoothed 1 s | **7.87** | 11.34 | 100 % | 0.294 | 0.78 |
| smoothed 2 s | **7.84** | 11.39 | 100 % | 0.280 | 0.74 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-413 | 6.5 (1.20) | 6.5 (0.88) | 6.6 (0.93) | 6.6 (0.72) | 6.5 (0.65) |
| run-414 | 9.4 (1.21) | 9.5 (0.91) | 9.5 (0.95) | 9.4 (0.77) | 9.5 (0.73) |
| run-415 | 8.0 (1.35) | 7.9 (0.98) | 7.9 (1.04) | 7.8 (0.80) | 7.8 (0.75) |
| run-416 | 7.8 (1.39) | 7.7 (1.02) | 7.7 (1.07) | 7.6 (0.83) | 7.6 (0.81) |
