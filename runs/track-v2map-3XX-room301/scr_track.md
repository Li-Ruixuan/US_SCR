# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/v2map-3XX-room301/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-3XX-room301/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.21** | 5.70 | 100 % | 1.429 | 1.87 |
| smoothed 0.25 s | **3.08** | 5.57 | 100 % | 0.653 | 1.46 |
| smoothed 0.5 s | **3.07** | 5.54 | 100 % | 0.656 | 1.52 |
| smoothed 1 s | **3.04** | 5.52 | 100 % | 0.446 | 1.24 |
| smoothed 2 s | **2.94** | 5.48 | 100 % | 0.437 | 1.17 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-315 | 3.9 (1.95) | 3.7 (1.55) | 3.6 (1.61) | 3.6 (1.33) | 3.5 (1.22) |
| run-316 | 2.4 (1.60) | 2.3 (1.21) | 2.3 (1.28) | 2.4 (1.00) | 2.2 (0.96) |
| run-317 | 3.4 (2.06) | 3.2 (1.62) | 3.2 (1.69) | 3.1 (1.38) | 3.1 (1.32) |
