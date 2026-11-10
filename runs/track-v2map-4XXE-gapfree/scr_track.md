# Single-model tracking: SCR alone on every 2th row (test_4XXE, `runs/v2map-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **7.16** | 10.85 | 95 % | 1.492 | 1.99 |
| smoothed 0.25 s | **7.05** | 10.74 | 100 % | 0.759 | 1.67 |
| smoothed 0.5 s | **7.06** | 10.77 | 100 % | 0.777 | 1.74 |
| smoothed 1 s | **7.06** | 10.66 | 100 % | 0.543 | 1.42 |
| smoothed 2 s | **7.07** | 10.69 | 100 % | 0.752 | 1.64 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-425 | 5.4 (2.22) | 5.3 (1.80) | 5.3 (1.89) | 5.3 (1.59) | 5.3 (1.59) |
| run-426 | 6.9 (2.12) | 7.0 (1.67) | 7.0 (1.75) | 6.9 (1.38) | 7.0 (1.43) |
| run-427 | 11.8 (1.97) | 11.6 (1.97) | 11.6 (2.02) | 11.6 (1.75) | 11.7 (2.62) |
| run-428 | 4.5 (1.64) | 4.4 (1.23) | 4.4 (1.30) | 4.4 (0.98) | 4.4 (0.91) |
