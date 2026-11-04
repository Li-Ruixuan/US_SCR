# Single-model tracking: SCR alone on every 2th row (test_4XXC, `runs/v2map-pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-pool-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **10.63** | 14.80 | 100 % | 0.998 | 1.21 |
| smoothed 0.25 s | **10.65** | 14.73 | 100 % | 0.424 | 0.90 |
| smoothed 0.5 s | **10.65** | 14.72 | 100 % | 0.429 | 0.94 |
| smoothed 1 s | **10.69** | 14.69 | 100 % | 0.288 | 0.76 |
| smoothed 2 s | **10.69** | 14.69 | 100 % | 0.280 | 0.73 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-413 | 10.0 (1.15) | 10.0 (0.82) | 10.0 (0.86) | 10.1 (0.66) | 10.1 (0.62) |
| run-414 | 11.1 (1.09) | 11.2 (0.85) | 11.2 (0.88) | 11.2 (0.74) | 11.2 (0.74) |
| run-415 | 10.9 (1.33) | 10.9 (0.97) | 10.9 (1.02) | 10.9 (0.80) | 11.0 (0.78) |
| run-416 | 10.5 (1.28) | 10.5 (0.98) | 10.5 (1.02) | 10.6 (0.83) | 10.6 (0.80) |
