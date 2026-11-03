# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/repro/v2map-3XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/repro/map-3XX/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.50** | 4.51 | 100 % | 1.316 | 1.60 |
| smoothed 0.25 s | **2.42** | 4.28 | 100 % | 0.569 | 1.19 |
| smoothed 0.5 s | **2.44** | 4.30 | 100 % | 0.573 | 1.26 |
| smoothed 1 s | **2.36** | 4.19 | 100 % | 0.366 | 0.98 |
| smoothed 2 s | **2.34** | 4.23 | 100 % | 0.349 | 0.90 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 3.0 (1.26) | 3.0 (0.91) | 3.0 (0.95) | 3.0 (0.73) | 3.0 (0.68) |
| run-314 | 2.5 (1.53) | 2.6 (1.07) | 2.5 (1.13) | 2.5 (0.82) | 2.5 (0.63) |
| run-315 | 2.3 (1.82) | 2.2 (1.38) | 2.2 (1.46) | 2.1 (1.19) | 2.1 (1.10) |
| run-316 | 1.9 (1.53) | 1.9 (1.16) | 1.8 (1.23) | 1.8 (0.94) | 1.7 (0.90) |
| run-317 | 2.8 (1.88) | 2.5 (1.44) | 2.5 (1.52) | 2.4 (1.22) | 2.4 (1.18) |
