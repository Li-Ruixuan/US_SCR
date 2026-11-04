# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/repro/v2map-3XX-seed1/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/repro/map-3XX-seed1/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.34** | 4.36 | 100 % | 1.306 | 1.60 |
| smoothed 0.25 s | **2.25** | 4.21 | 100 % | 0.561 | 1.20 |
| smoothed 0.5 s | **2.25** | 4.23 | 100 % | 0.567 | 1.26 |
| smoothed 1 s | **2.21** | 4.19 | 100 % | 0.368 | 0.99 |
| smoothed 2 s | **2.22** | 4.19 | 100 % | 0.354 | 0.92 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 2.4 (1.28) | 2.4 (0.94) | 2.4 (0.98) | 2.4 (0.77) | 2.5 (0.72) |
| run-314 | 2.3 (1.53) | 2.3 (1.07) | 2.3 (1.14) | 2.3 (0.84) | 2.4 (0.65) |
| run-315 | 2.4 (1.81) | 2.2 (1.39) | 2.2 (1.47) | 2.1 (1.20) | 2.1 (1.13) |
| run-316 | 1.9 (1.49) | 1.8 (1.14) | 1.8 (1.20) | 1.7 (0.93) | 1.7 (0.89) |
| run-317 | 2.7 (1.90) | 2.5 (1.44) | 2.5 (1.52) | 2.4 (1.24) | 2.4 (1.22) |
