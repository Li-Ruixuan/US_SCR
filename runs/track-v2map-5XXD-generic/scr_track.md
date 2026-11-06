# Single-model tracking: SCR alone on every 2th row (test_5XXD, `runs/v2map-5XXC-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-generic/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.15** | 6.48 | 100 % | 0.959 | 1.29 |
| smoothed 0.25 s | **5.11** | 6.38 | 100 % | 0.471 | 1.02 |
| smoothed 0.5 s | **5.11** | 6.37 | 100 % | 0.485 | 1.07 |
| smoothed 1 s | **5.07** | 6.36 | 100 % | 0.296 | 0.81 |
| smoothed 2 s | **5.09** | 6.33 | 100 % | 0.262 | 0.70 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-525 | 4.5 (1.29) | 4.5 (0.96) | 4.5 (1.02) | 4.4 (0.74) | 4.4 (0.58) |
| run-526 | 5.5 (1.20) | 5.5 (0.95) | 5.5 (1.00) | 5.4 (0.74) | 5.4 (0.60) |
| run-527 | 5.5 (1.39) | 5.5 (1.12) | 5.5 (1.17) | 5.4 (0.89) | 5.5 (0.84) |
| run-528 | 5.1 (1.30) | 5.1 (1.06) | 5.1 (1.11) | 5.0 (0.87) | 5.0 (0.78) |
