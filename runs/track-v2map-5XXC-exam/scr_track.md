# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXC-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.13** | 5.21 | 100 % | 0.620 | 0.80 |
| smoothed 0.25 s | **3.12** | 5.11 | 100 % | 0.293 | 0.62 |
| smoothed 0.5 s | **3.13** | 5.12 | 100 % | 0.295 | 0.65 |
| smoothed 1 s | **3.11** | 5.08 | 100 % | 0.190 | 0.51 |
| smoothed 2 s | **3.09** | 5.03 | 100 % | 0.171 | 0.45 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | 3.6 (0.63) | 3.6 (0.47) | 3.6 (0.49) | 3.5 (0.38) | 3.6 (0.35) |
| run-518 | 2.5 (0.55) | 2.5 (0.41) | 2.5 (0.43) | 2.5 (0.33) | 2.5 (0.27) |
| run-519 | 2.6 (0.61) | 2.6 (0.48) | 2.6 (0.50) | 2.6 (0.41) | 2.6 (0.37) |
| run-520 | 5.2 (0.95) | 5.2 (0.77) | 5.3 (0.80) | 5.1 (0.65) | 5.0 (0.59) |
| run-521 | 2.7 (0.70) | 2.7 (0.54) | 2.7 (0.57) | 2.7 (0.45) | 2.7 (0.39) |
| run-522 | 2.0 (0.66) | 2.0 (0.51) | 2.0 (0.53) | 2.0 (0.43) | 2.0 (0.38) |
| run-523 | 3.4 (1.34) | 3.3 (1.08) | 3.3 (1.12) | 3.4 (0.89) | 3.4 (0.76) |
| run-524 | 3.0 (0.94) | 3.0 (0.69) | 3.0 (0.73) | 3.0 (0.56) | 3.0 (0.45) |
