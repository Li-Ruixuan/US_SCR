# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXB-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-generic/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **19.05** | 26.29 | 18 % | 6.599 | 7.20 |
| smoothed 0.25 s | **41.06** | 83.78 | 96 % | 1.954 | 3.72 |
| smoothed 0.5 s | **41.05** | 83.78 | 96 % | 1.927 | 3.74 |
| smoothed 1 s | **40.85** | 83.78 | 96 % | 1.652 | 3.38 |
| smoothed 2 s | **40.70** | 83.77 | 96 % | 1.512 | 3.06 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | 30.6 (7.89) | 36.1 (6.87) | 36.0 (6.91) | 35.5 (6.49) | 35.0 (6.21) |
| run-518 | 19.2 (7.54) | 63.9 (1.72) | 63.9 (1.74) | 63.9 (1.60) | 63.9 (1.50) |
| run-519 | 20.0 (4.26) | 27.3 (3.22) | 27.3 (3.20) | 26.9 (2.93) | 26.9 (2.80) |
| run-520 | 19.8 (12.08) | 45.1 (5.80) | 45.0 (5.75) | 44.7 (4.94) | 44.4 (4.15) |
| run-521 | 21.0 (5.01) | 67.8 (2.14) | 67.8 (2.12) | 67.8 (1.92) | 67.8 (1.78) |
| run-522 | 27.6 (10.12) | 61.9 (2.47) | 61.9 (2.48) | 61.9 (2.35) | 61.9 (2.35) |
| run-523 | 8.1 (6.97) | 13.8 (4.65) | 13.8 (4.82) | 13.4 (4.07) | 13.2 (3.07) |
| run-524 | 6.1 (3.71) | 12.6 (2.86) | 12.7 (2.87) | 12.6 (2.73) | 12.4 (2.61) |
