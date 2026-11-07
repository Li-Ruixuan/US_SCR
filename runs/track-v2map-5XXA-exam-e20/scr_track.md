# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-exam-e20/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.65** | 4.90 | 100 % | 1.336 | 1.59 |
| smoothed 0.25 s | **2.55** | 4.74 | 100 % | 0.540 | 1.15 |
| smoothed 0.5 s | **2.56** | 4.73 | 100 % | 0.547 | 1.21 |
| smoothed 1 s | **2.53** | 4.66 | 100 % | 0.300 | 0.89 |
| smoothed 2 s | **2.53** | 4.65 | 100 % | 0.231 | 0.67 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.4 (1.49) | 2.3 (1.06) | 2.3 (1.12) | 2.2 (0.83) | 2.2 (0.58) |
| run-502 | 2.2 (1.39) | 2.1 (1.02) | 2.1 (1.08) | 2.1 (0.83) | 2.1 (0.68) |
| run-503 | 2.5 (1.51) | 2.4 (1.10) | 2.4 (1.16) | 2.3 (0.85) | 2.3 (0.62) |
| run-504 | 3.4 (2.00) | 3.4 (1.46) | 3.4 (1.52) | 3.4 (1.16) | 3.3 (0.94) |
| run-505 | 3.2 (1.86) | 3.1 (1.42) | 3.1 (1.49) | 3.1 (1.15) | 3.1 (0.92) |
| run-506 | 2.8 (1.60) | 2.7 (1.13) | 2.7 (1.19) | 2.7 (0.87) | 2.7 (0.62) |
| run-507 | 2.7 (1.52) | 2.6 (1.00) | 2.6 (1.07) | 2.6 (0.73) | 2.6 (0.50) |
| run-508 | 2.0 (1.33) | 1.9 (0.97) | 1.9 (1.02) | 1.8 (0.73) | 1.9 (0.51) |
