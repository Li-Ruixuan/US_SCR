# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/repro/v2map-3XX-seed2/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/repro/map-3XX-seed2/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.37** | 4.58 | 100 % | 1.321 | 1.62 |
| smoothed 0.25 s | **2.28** | 4.49 | 100 % | 0.564 | 1.21 |
| smoothed 0.5 s | **2.31** | 4.50 | 100 % | 0.569 | 1.28 |
| smoothed 1 s | **2.23** | 4.42 | 100 % | 0.370 | 1.00 |
| smoothed 2 s | **2.25** | 4.40 | 100 % | 0.354 | 0.92 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 2.6 (1.28) | 2.6 (0.94) | 2.6 (0.99) | 2.6 (0.76) | 2.6 (0.71) |
| run-314 | 2.5 (1.52) | 2.4 (1.05) | 2.4 (1.12) | 2.3 (0.81) | 2.5 (0.62) |
| run-315 | 2.2 (1.87) | 2.0 (1.47) | 2.0 (1.54) | 2.0 (1.27) | 1.9 (1.20) |
| run-316 | 1.9 (1.50) | 1.9 (1.13) | 1.9 (1.20) | 1.8 (0.92) | 1.8 (0.90) |
| run-317 | 2.6 (1.92) | 2.6 (1.47) | 2.6 (1.55) | 2.5 (1.26) | 2.4 (1.20) |
