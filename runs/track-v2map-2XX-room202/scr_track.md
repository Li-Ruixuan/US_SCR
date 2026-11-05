# Single-model tracking: SCR alone on every 2th row (train_2XX, `runs/v2map-2XX-room202/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-2XX-room202/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **22.57** | 29.48 | 58 % | 7.380 | 8.34 |
| smoothed 0.25 s | **24.16** | 37.44 | 100 % | 6.695 | 10.21 |
| smoothed 0.5 s | **24.21** | 37.38 | 100 % | 6.673 | 10.38 |
| smoothed 1 s | **23.81** | 37.07 | 100 % | 5.811 | 9.09 |
| smoothed 2 s | **23.62** | 36.68 | 100 % | 4.750 | 7.54 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-205 | 21.0 (10.68) | 21.5 (10.88) | 21.7 (11.26) | 21.2 (9.12) | 20.9 (6.28) |
| run-211 | 24.2 (6.00) | 26.8 (9.53) | 26.7 (9.51) | 26.4 (9.07) | 26.3 (8.80) |
