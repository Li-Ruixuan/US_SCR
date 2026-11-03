# Single-model tracking: SCR alone on every 2th row (test_4XXA, `runs/v2map-4XXA/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXA/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.07** | 9.15 | 100 % | 1.326 | 1.73 |
| smoothed 0.25 s | **5.02** | 9.05 | 100 % | 0.606 | 1.36 |
| smoothed 0.5 s | **5.03** | 9.05 | 100 % | 0.605 | 1.41 |
| smoothed 1 s | **5.02** | 9.04 | 100 % | 0.403 | 1.16 |
| smoothed 2 s | **5.04** | 8.97 | 100 % | 0.373 | 1.07 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-401 | 4.5 (1.96) | 4.3 (1.52) | 4.4 (1.58) | 4.4 (1.35) | 4.4 (1.42) |
| run-402 | 6.9 (1.24) | 6.9 (0.88) | 6.9 (0.92) | 6.9 (0.72) | 7.0 (0.70) |
| run-403 | 4.1 (1.32) | 4.0 (0.95) | 4.0 (0.99) | 4.0 (0.75) | 4.0 (0.60) |
| run-404 | 6.5 (1.97) | 6.6 (1.58) | 6.6 (1.63) | 6.7 (1.28) | 6.6 (1.06) |
| run-405 | 6.5 (1.75) | 6.5 (1.34) | 6.5 (1.41) | 6.5 (1.13) | 6.5 (1.05) |
| run-406 | 3.0 (1.63) | 2.9 (1.30) | 2.9 (1.34) | 2.8 (1.13) | 2.8 (1.00) |
| run-407 | 4.1 (1.42) | 4.1 (1.11) | 4.1 (1.16) | 4.1 (0.94) | 4.1 (0.88) |
| run-408 | 4.9 (2.55) | 4.8 (2.19) | 4.8 (2.24) | 4.8 (2.01) | 4.8 (1.86) |
