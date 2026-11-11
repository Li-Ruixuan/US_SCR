# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXC-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.57** | 7.19 | 100 % | 0.729 | 1.04 |
| smoothed 0.25 s | **3.54** | 7.14 | 100 % | 0.360 | 0.84 |
| smoothed 0.5 s | **3.54** | 7.14 | 100 % | 0.363 | 0.87 |
| smoothed 1 s | **3.54** | 7.09 | 100 % | 0.244 | 0.72 |
| smoothed 2 s | **3.53** | 7.00 | 100 % | 0.214 | 0.63 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | 4.1 (0.89) | 4.0 (0.71) | 4.0 (0.74) | 3.9 (0.62) | 3.9 (0.57) |
| run-518 | 2.8 (0.81) | 2.8 (0.64) | 2.8 (0.67) | 2.8 (0.55) | 2.8 (0.48) |
| run-519 | 3.0 (0.85) | 3.0 (0.68) | 3.0 (0.71) | 3.0 (0.60) | 3.0 (0.54) |
| run-520 | 6.0 (1.15) | 6.0 (0.96) | 6.0 (0.99) | 6.1 (0.84) | 6.0 (0.74) |
| run-521 | 3.0 (0.94) | 3.0 (0.75) | 3.0 (0.78) | 3.0 (0.64) | 3.0 (0.57) |
| run-522 | 2.5 (0.89) | 2.4 (0.71) | 2.4 (0.74) | 2.4 (0.62) | 2.5 (0.55) |
| run-523 | 3.9 (1.60) | 3.9 (1.31) | 3.9 (1.37) | 3.9 (1.11) | 3.8 (0.94) |
| run-524 | 3.2 (1.18) | 3.2 (0.92) | 3.2 (0.96) | 3.1 (0.77) | 3.1 (0.64) |
