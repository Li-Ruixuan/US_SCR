# Single-model tracking: SCR alone on every 2th row (test_4XXD, `runs/v2map-pool-4XXC/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-pool-4XXC/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **14.07** | 22.87 | 97 % | 1.585 | 2.19 |
| smoothed 0.25 s | **14.08** | 22.94 | 100 % | 0.761 | 1.85 |
| smoothed 0.5 s | **14.08** | 22.89 | 100 % | 0.776 | 1.92 |
| smoothed 1 s | **14.06** | 23.03 | 100 % | 0.549 | 1.64 |
| smoothed 2 s | **14.00** | 22.69 | 100 % | 0.525 | 1.59 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-418 | 14.6 (1.29) | 14.6 (0.99) | 14.6 (1.03) | 14.5 (0.82) | 14.6 (0.77) |
| run-419 | 14.2 (1.44) | 14.1 (1.15) | 14.1 (1.22) | 14.1 (0.95) | 14.0 (1.02) |
| run-420 | 17.7 (2.18) | 18.3 (1.89) | 18.3 (1.95) | 18.2 (1.67) | 18.1 (1.60) |
| run-421 | 15.6 (2.14) | 15.3 (2.09) | 15.3 (2.16) | 15.3 (1.89) | 15.3 (1.87) |
| run-423 | 9.8 (4.98) | 9.7 (4.18) | 9.7 (4.32) | 9.7 (3.90) | 9.6 (3.71) |
| run-424 | 12.5 (1.08) | 12.5 (0.80) | 12.5 (0.86) | 12.5 (0.62) | 12.5 (0.54) |
