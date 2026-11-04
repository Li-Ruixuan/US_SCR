# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/repro/v2map-3XX-nocalib/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/repro/map-3XX-nocalib/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **11.45** | 13.64 | 100 % | 1.342 | 1.74 |
| smoothed 0.25 s | **11.46** | 13.45 | 100 % | 0.598 | 1.34 |
| smoothed 0.5 s | **11.45** | 13.47 | 100 % | 0.602 | 1.41 |
| smoothed 1 s | **11.45** | 13.39 | 100 % | 0.400 | 1.15 |
| smoothed 2 s | **11.49** | 13.40 | 100 % | 0.382 | 1.06 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 11.8 (1.32) | 11.9 (0.94) | 11.9 (0.98) | 11.9 (0.75) | 11.9 (0.71) |
| run-314 | 10.8 (1.58) | 10.8 (1.12) | 10.8 (1.18) | 10.8 (0.88) | 10.9 (0.66) |
| run-315 | 11.4 (1.96) | 11.4 (1.56) | 11.4 (1.63) | 11.4 (1.37) | 11.5 (1.26) |
| run-316 | 10.7 (1.62) | 10.6 (1.27) | 10.7 (1.33) | 10.7 (1.08) | 10.6 (1.06) |
| run-317 | 12.6 (2.23) | 12.5 (1.84) | 12.4 (1.91) | 12.4 (1.65) | 12.6 (1.62) |
