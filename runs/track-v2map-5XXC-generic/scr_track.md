# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXC-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-generic/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **6.36** | 8.29 | 100 % | 0.636 | 0.84 |
| smoothed 0.25 s | **6.35** | 8.29 | 100 % | 0.303 | 0.66 |
| smoothed 0.5 s | **6.36** | 8.29 | 100 % | 0.307 | 0.69 |
| smoothed 1 s | **6.35** | 8.29 | 100 % | 0.198 | 0.54 |
| smoothed 2 s | **6.32** | 8.27 | 100 % | 0.176 | 0.47 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | 7.4 (0.66) | 7.4 (0.50) | 7.4 (0.52) | 7.4 (0.41) | 7.4 (0.38) |
| run-518 | 7.0 (0.58) | 7.0 (0.43) | 7.0 (0.45) | 7.0 (0.35) | 7.0 (0.29) |
| run-519 | 6.3 (0.66) | 6.3 (0.52) | 6.3 (0.54) | 6.3 (0.44) | 6.3 (0.38) |
| run-520 | 7.0 (1.05) | 7.0 (0.85) | 7.0 (0.88) | 6.9 (0.73) | 6.9 (0.64) |
| run-521 | 6.8 (0.73) | 6.8 (0.58) | 6.8 (0.61) | 6.8 (0.49) | 6.8 (0.43) |
| run-522 | 5.8 (0.68) | 5.8 (0.53) | 5.8 (0.55) | 5.8 (0.45) | 5.8 (0.39) |
| run-523 | 5.9 (1.41) | 5.9 (1.16) | 5.9 (1.22) | 5.8 (0.96) | 5.7 (0.81) |
| run-524 | 4.7 (0.92) | 4.7 (0.68) | 4.7 (0.71) | 4.7 (0.53) | 4.7 (0.41) |
