# Single-model tracking: SCR alone on every 2th row (test_5XXE, `runs/v2map-5XXE-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXE-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.89** | 9.45 | 100 % | 0.718 | 1.01 |
| smoothed 0.25 s | **5.87** | 9.41 | 100 % | 0.364 | 0.84 |
| smoothed 0.5 s | **5.87** | 9.40 | 100 % | 0.371 | 0.88 |
| smoothed 1 s | **5.85** | 9.36 | 100 % | 0.244 | 0.73 |
| smoothed 2 s | **5.86** | 9.38 | 100 % | 0.219 | 0.64 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-529 | 5.2 (0.96) | 5.2 (0.78) | 5.2 (0.82) | 5.1 (0.67) | 5.2 (0.55) |
| run-530 | 5.6 (0.85) | 5.6 (0.66) | 5.6 (0.69) | 5.5 (0.55) | 5.5 (0.47) |
| run-531 | 7.3 (1.18) | 7.4 (1.07) | 7.4 (1.12) | 7.4 (0.98) | 7.4 (0.95) |
| run-532 | 5.5 (1.05) | 5.4 (0.85) | 5.4 (0.89) | 5.3 (0.71) | 5.3 (0.61) |
