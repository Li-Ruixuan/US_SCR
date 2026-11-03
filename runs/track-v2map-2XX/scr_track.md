# Single-model tracking: SCR alone on every 2th row (train_2XX, `runs/v2map-2XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-2XX/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **8.43** | 21.39 | 100 % | 2.458 | 3.86 |
| smoothed 0.25 s | **8.24** | 21.97 | 100 % | 1.213 | 3.25 |
| smoothed 0.5 s | **8.22** | 21.90 | 100 % | 1.197 | 3.33 |
| smoothed 1 s | **8.13** | 21.51 | 100 % | 0.838 | 2.93 |
| smoothed 2 s | **8.06** | 21.58 | 100 % | 0.724 | 2.57 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-205 | 9.0 (5.55) | 8.9 (4.96) | 8.9 (5.05) | 8.7 (4.70) | 8.7 (4.27) |
| run-211 | 7.8 (2.16) | 7.6 (1.53) | 7.6 (1.60) | 7.5 (1.17) | 7.4 (0.87) |
