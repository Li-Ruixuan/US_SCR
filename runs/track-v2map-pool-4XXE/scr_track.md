# Single-model tracking: SCR alone on every 2th row (test_4XXE, `runs/v2map-pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-pool-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **10.57** | 15.34 | 95 % | 1.516 | 1.98 |
| smoothed 0.25 s | **10.58** | 16.11 | 100 % | 0.918 | 1.82 |
| smoothed 0.5 s | **10.56** | 16.08 | 100 % | 0.931 | 1.89 |
| smoothed 1 s | **10.57** | 16.00 | 100 % | 0.704 | 1.58 |
| smoothed 2 s | **10.62** | 15.96 | 100 % | 0.708 | 1.61 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-425 | 8.6 (2.08) | 8.5 (1.68) | 8.5 (1.76) | 8.5 (1.48) | 8.7 (1.59) |
| run-426 | 10.3 (2.16) | 10.3 (1.70) | 10.2 (1.78) | 10.3 (1.43) | 10.3 (1.45) |
| run-427 | 15.0 (2.13) | 15.2 (2.78) | 15.2 (2.82) | 15.2 (2.51) | 15.2 (2.52) |
| run-428 | 8.4 (1.54) | 8.3 (1.13) | 8.3 (1.19) | 8.3 (0.91) | 8.3 (0.88) |
