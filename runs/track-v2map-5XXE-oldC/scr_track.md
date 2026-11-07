# Single-model tracking: SCR alone on every 2th row (test_5XXE, `runs/v2map-5XXC-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **9.25** | 19.66 | 56 % | 4.713 | 4.85 |
| smoothed 0.25 s | **14.16** | 47.04 | 100 % | 2.144 | 4.20 |
| smoothed 0.5 s | **14.14** | 46.80 | 100 % | 2.080 | 4.15 |
| smoothed 1 s | **13.88** | 46.63 | 100 % | 1.567 | 3.55 |
| smoothed 2 s | **13.61** | 46.42 | 100 % | 1.405 | 3.07 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-529 | 9.3 (5.03) | 10.0 (4.09) | 10.0 (4.15) | 9.9 (3.32) | 9.8 (2.64) |
| run-530 | 9.4 (3.00) | 15.9 (3.17) | 15.9 (3.20) | 15.9 (2.83) | 15.6 (2.53) |
| run-531 | 7.4 (2.82) | 10.4 (3.49) | 10.5 (3.25) | 10.2 (2.93) | 10.5 (2.56) |
| run-532 | 11.0 (8.56) | 20.4 (6.07) | 20.2 (6.00) | 19.5 (5.13) | 18.5 (4.54) |
