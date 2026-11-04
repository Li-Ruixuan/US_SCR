# Single-model tracking: SCR alone on every 2th row (train_2XX, `runs/v2map-2XX-strictjoin/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-2XX-strictjoin/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **9.61** | 17.76 | 100 % | 2.574 | 3.62 |
| smoothed 0.25 s | **9.59** | 17.66 | 100 % | 1.154 | 2.90 |
| smoothed 0.5 s | **9.54** | 17.70 | 100 % | 1.128 | 2.96 |
| smoothed 1 s | **9.52** | 17.55 | 100 % | 0.736 | 2.54 |
| smoothed 2 s | **9.49** | 17.45 | 100 % | 0.621 | 2.18 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-205 | 14.3 (4.99) | 14.2 (4.19) | 14.2 (4.24) | 14.2 (3.80) | 14.2 (3.41) |
| run-211 | 4.9 (2.25) | 4.9 (1.61) | 4.9 (1.68) | 4.9 (1.27) | 4.8 (0.96) |
