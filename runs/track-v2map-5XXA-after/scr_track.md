# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-after/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-after/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.65** | 5.51 | 100 % | 1.286 | 1.55 |
| smoothed 0.25 s | **2.53** | 5.31 | 100 % | 0.527 | 1.12 |
| smoothed 0.5 s | **2.55** | 5.33 | 100 % | 0.534 | 1.18 |
| smoothed 1 s | **2.50** | 5.26 | 100 % | 0.294 | 0.88 |
| smoothed 2 s | **2.48** | 5.24 | 100 % | 0.232 | 0.67 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.1 (1.38) | 2.0 (0.98) | 2.0 (1.04) | 2.0 (0.77) | 1.9 (0.54) |
| run-502 | 1.9 (1.31) | 1.8 (0.94) | 1.8 (0.99) | 1.8 (0.75) | 1.8 (0.63) |
| run-503 | 2.8 (1.41) | 2.8 (1.02) | 2.8 (1.07) | 2.7 (0.80) | 2.6 (0.63) |
| run-504 | 4.1 (2.00) | 3.9 (1.51) | 4.0 (1.57) | 3.9 (1.21) | 4.0 (1.01) |
| run-505 | 2.9 (1.93) | 2.7 (1.49) | 2.8 (1.56) | 2.7 (1.21) | 2.6 (0.96) |
| run-506 | 1.9 (1.49) | 1.7 (1.07) | 1.7 (1.13) | 1.7 (0.82) | 1.6 (0.59) |
| run-507 | 3.2 (1.56) | 3.2 (1.02) | 3.2 (1.09) | 3.2 (0.75) | 3.2 (0.52) |
| run-508 | 2.2 (1.29) | 2.1 (0.91) | 2.1 (0.96) | 2.1 (0.68) | 2.1 (0.48) |
