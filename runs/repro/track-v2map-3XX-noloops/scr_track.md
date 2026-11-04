# Single-model tracking: SCR alone on every 2th row (train_3XX, `runs/repro/v2map-3XX-noloops/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/repro/map-3XX-noloops/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.90** | 9.13 | 100 % | 1.383 | 1.81 |
| smoothed 0.25 s | **5.88** | 9.00 | 100 % | 0.612 | 1.40 |
| smoothed 0.5 s | **5.88** | 8.99 | 100 % | 0.620 | 1.47 |
| smoothed 1 s | **5.84** | 8.90 | 100 % | 0.412 | 1.18 |
| smoothed 2 s | **5.76** | 8.95 | 100 % | 0.383 | 1.05 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-313 | 6.9 (1.39) | 6.9 (1.02) | 6.8 (1.07) | 6.8 (0.82) | 6.8 (0.73) |
| run-314 | 7.8 (1.63) | 7.8 (1.17) | 7.8 (1.23) | 7.7 (0.94) | 7.7 (0.72) |
| run-315 | 4.8 (2.06) | 4.8 (1.66) | 4.7 (1.74) | 4.7 (1.43) | 4.7 (1.27) |
| run-316 | 4.6 (1.69) | 4.5 (1.34) | 4.5 (1.40) | 4.6 (1.15) | 4.5 (1.05) |
| run-317 | 5.3 (2.26) | 5.4 (1.81) | 5.4 (1.90) | 5.4 (1.55) | 5.0 (1.47) |
