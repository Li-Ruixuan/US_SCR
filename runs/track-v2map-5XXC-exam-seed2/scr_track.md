# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXC-exam-seed2/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.31** | 5.45 | 100 % | 0.626 | 0.81 |
| smoothed 0.25 s | **3.30** | 5.39 | 100 % | 0.295 | 0.62 |
| smoothed 0.5 s | **3.31** | 5.40 | 100 % | 0.297 | 0.65 |
| smoothed 1 s | **3.30** | 5.36 | 100 % | 0.191 | 0.52 |
| smoothed 2 s | **3.27** | 5.31 | 100 % | 0.172 | 0.45 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | 3.9 (0.64) | 3.9 (0.48) | 3.9 (0.50) | 3.9 (0.39) | 3.9 (0.37) |
| run-518 | 2.8 (0.55) | 2.8 (0.41) | 2.8 (0.43) | 2.8 (0.33) | 2.8 (0.27) |
| run-519 | 2.8 (0.61) | 2.8 (0.48) | 2.8 (0.50) | 2.8 (0.41) | 2.8 (0.37) |
| run-520 | 5.4 (0.96) | 5.3 (0.78) | 5.3 (0.82) | 5.3 (0.67) | 5.1 (0.60) |
| run-521 | 2.9 (0.71) | 2.8 (0.54) | 2.8 (0.56) | 2.8 (0.45) | 2.8 (0.40) |
| run-522 | 2.2 (0.65) | 2.1 (0.51) | 2.1 (0.52) | 2.1 (0.43) | 2.1 (0.38) |
| run-523 | 3.7 (1.38) | 3.7 (1.09) | 3.7 (1.14) | 3.7 (0.90) | 3.7 (0.76) |
| run-524 | 3.0 (0.95) | 2.9 (0.71) | 2.9 (0.74) | 3.0 (0.57) | 3.0 (0.45) |
