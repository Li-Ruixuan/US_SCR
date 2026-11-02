# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2calib-3XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `runs/map-3XX-calib/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.66** | 6.28 | 100 % | 1.373 | 1.74 |
| smoothed 0.25 s | **3.60** | 6.14 | 100 % | 0.600 | 1.34 |
| smoothed 0.5 s | **3.63** | 6.13 | 100 % | 0.606 | 1.40 |
| smoothed 1 s | **3.57** | 6.08 | 100 % | 0.398 | 1.12 |
| smoothed 2 s | **3.60** | 6.13 | 100 % | 0.373 | 1.01 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 2.6 (1.36) | 2.6 (0.99) | 2.6 (1.04) | 2.6 (0.81) | 2.5 (0.72) |
| run-314 | 3.4 (1.68) | 3.3 (1.23) | 3.3 (1.29) | 3.3 (0.97) | 3.3 (0.74) |
| run-315 | 3.3 (1.95) | 3.2 (1.54) | 3.2 (1.62) | 3.1 (1.32) | 3.2 (1.23) |
| run-316 | 3.8 (1.67) | 3.8 (1.31) | 3.8 (1.38) | 3.6 (1.13) | 3.7 (1.07) |
| run-317 | 5.3 (2.06) | 5.2 (1.62) | 5.3 (1.69) | 5.3 (1.39) | 5.3 (1.31) |
