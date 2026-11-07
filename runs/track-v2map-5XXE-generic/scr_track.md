# Single-model tracking: SCR alone on every 2th row (test_5XXE, `runs/v2map-5XXE-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXE-generic/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **12.99** | 15.12 | 100 % | 0.758 | 1.01 |
| smoothed 0.25 s | **13.00** | 15.10 | 100 % | 0.356 | 0.81 |
| smoothed 0.5 s | **13.00** | 15.09 | 100 % | 0.363 | 0.84 |
| smoothed 1 s | **13.03** | 15.07 | 100 % | 0.237 | 0.68 |
| smoothed 2 s | **13.07** | 15.09 | 100 % | 0.213 | 0.59 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-529 | 14.9 (1.06) | 14.9 (0.86) | 15.0 (0.90) | 15.0 (0.73) | 15.1 (0.62) |
| run-530 | 11.7 (0.83) | 11.7 (0.63) | 11.7 (0.66) | 11.7 (0.50) | 11.7 (0.41) |
| run-531 | 11.8 (1.13) | 11.8 (0.91) | 11.8 (0.95) | 11.9 (0.78) | 11.9 (0.73) |
| run-532 | 13.5 (1.04) | 13.6 (0.83) | 13.5 (0.86) | 13.6 (0.69) | 13.7 (0.59) |
