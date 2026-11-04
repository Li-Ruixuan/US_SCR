# Single-model tracking: SCR alone on every 2th row (test_4XXD, `runs/v2map-4XXC-owncalib/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-4XXC-owncalib/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **9.65** | 15.17 | 97 % | 1.401 | 1.78 |
| smoothed 0.25 s | **9.61** | 15.23 | 100 % | 0.749 | 1.57 |
| smoothed 0.5 s | **9.61** | 15.26 | 100 % | 0.736 | 1.61 |
| smoothed 1 s | **9.58** | 15.23 | 100 % | 0.501 | 1.30 |
| smoothed 2 s | **9.58** | 15.17 | 100 % | 0.458 | 1.19 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-418 | 10.1 (1.33) | 10.0 (1.03) | 10.1 (1.07) | 10.0 (0.84) | 10.0 (0.79) |
| run-419 | 10.7 (1.61) | 10.6 (1.30) | 10.6 (1.37) | 10.6 (1.06) | 10.6 (1.04) |
| run-420 | 12.7 (1.98) | 12.7 (2.04) | 12.7 (2.06) | 12.7 (1.76) | 12.6 (1.64) |
| run-421 | 9.0 (2.29) | 8.9 (2.12) | 8.9 (2.19) | 8.9 (1.78) | 9.0 (1.63) |
| run-423 | 6.3 (2.40) | 6.3 (2.13) | 6.2 (2.11) | 6.2 (1.77) | 6.2 (1.51) |
| run-424 | 9.1 (1.09) | 9.1 (0.78) | 9.1 (0.84) | 9.1 (0.60) | 9.1 (0.54) |
