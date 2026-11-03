# Single-model tracking: SCR alone on every 2th row (test_4XXB, `runs/v2map-4XXB/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXB/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **6.57** | 8.18 | 100 % | 1.280 | 1.57 |
| smoothed 0.25 s | **6.54** | 7.98 | 100 % | 0.556 | 1.18 |
| smoothed 0.5 s | **6.53** | 7.97 | 100 % | 0.553 | 1.23 |
| smoothed 1 s | **6.54** | 7.94 | 100 % | 0.353 | 0.98 |
| smoothed 2 s | **6.55** | 7.89 | 100 % | 0.321 | 0.87 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-409 | 6.9 (1.44) | 6.9 (1.04) | 6.9 (1.09) | 6.9 (0.87) | 6.9 (0.93) |
| run-410 | 5.9 (1.39) | 5.9 (1.02) | 5.9 (1.07) | 5.9 (0.83) | 5.9 (0.73) |
| run-411 | 5.8 (1.88) | 5.8 (1.44) | 5.8 (1.51) | 5.8 (1.20) | 5.9 (0.95) |
| run-412 | 7.6 (1.56) | 7.5 (1.20) | 7.5 (1.23) | 7.5 (1.00) | 7.5 (0.88) |
