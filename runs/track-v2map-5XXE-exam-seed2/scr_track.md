# Single-model tracking: SCR alone on every 2th row (test_5XXE, `runs/v2map-5XXE-exam-seed2/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXE-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.84** | 9.68 | 100 % | 0.710 | 1.00 |
| smoothed 0.25 s | **5.85** | 9.67 | 100 % | 0.364 | 0.85 |
| smoothed 0.5 s | **5.86** | 9.65 | 100 % | 0.372 | 0.88 |
| smoothed 1 s | **5.84** | 9.61 | 100 % | 0.242 | 0.72 |
| smoothed 2 s | **5.86** | 9.57 | 100 % | 0.217 | 0.63 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-529 | 5.2 (0.95) | 5.1 (0.77) | 5.1 (0.80) | 5.1 (0.64) | 5.2 (0.55) |
| run-530 | 5.5 (0.85) | 5.5 (0.66) | 5.5 (0.69) | 5.5 (0.56) | 5.6 (0.48) |
| run-531 | 7.3 (1.14) | 7.3 (1.11) | 7.3 (1.15) | 7.3 (0.97) | 7.3 (0.92) |
| run-532 | 5.5 (1.05) | 5.4 (0.86) | 5.4 (0.89) | 5.4 (0.70) | 5.4 (0.60) |
