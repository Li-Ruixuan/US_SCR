# Single-model tracking: SCR alone on every 2th row (test_4XXD, `runs/v2map-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **11.73** | 16.63 | 97 % | 1.367 | 1.76 |
| smoothed 0.25 s | **11.54** | 16.68 | 100 % | 0.665 | 1.47 |
| smoothed 0.5 s | **11.54** | 16.70 | 100 % | 0.669 | 1.53 |
| smoothed 1 s | **11.51** | 16.74 | 100 % | 0.430 | 1.23 |
| smoothed 2 s | **11.54** | 16.70 | 100 % | 0.391 | 1.12 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-418 | 11.9 (1.37) | 11.8 (1.05) | 11.8 (1.10) | 11.8 (0.86) | 11.8 (0.77) |
| run-419 | 12.0 (1.57) | 11.8 (1.25) | 11.8 (1.32) | 11.7 (1.02) | 11.7 (1.02) |
| run-420 | 15.6 (2.04) | 15.0 (1.83) | 15.0 (1.85) | 15.1 (1.54) | 15.1 (1.40) |
| run-421 | 12.3 (2.29) | 12.1 (1.92) | 12.1 (2.00) | 12.1 (1.64) | 12.2 (1.55) |
| run-423 | 8.1 (2.20) | 8.1 (1.98) | 8.1 (2.04) | 8.0 (1.68) | 8.1 (1.45) |
| run-424 | 10.5 (1.11) | 10.4 (0.80) | 10.4 (0.86) | 10.4 (0.62) | 10.4 (0.55) |
