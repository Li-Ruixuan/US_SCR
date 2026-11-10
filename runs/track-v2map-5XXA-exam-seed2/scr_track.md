# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-exam-seed2/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.37** | 4.89 | 100 % | 1.241 | 1.49 |
| smoothed 0.25 s | **2.26** | 4.73 | 100 % | 0.510 | 1.09 |
| smoothed 0.5 s | **2.27** | 4.73 | 100 % | 0.517 | 1.14 |
| smoothed 1 s | **2.23** | 4.70 | 100 % | 0.289 | 0.85 |
| smoothed 2 s | **2.20** | 4.62 | 100 % | 0.226 | 0.65 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.4 (1.37) | 2.3 (0.98) | 2.3 (1.04) | 2.3 (0.76) | 2.3 (0.53) |
| run-502 | 1.9 (1.25) | 1.8 (0.92) | 1.8 (0.97) | 1.8 (0.74) | 1.8 (0.63) |
| run-503 | 2.4 (1.41) | 2.2 (1.04) | 2.2 (1.09) | 2.2 (0.82) | 2.2 (0.63) |
| run-504 | 2.9 (2.01) | 2.8 (1.49) | 2.8 (1.54) | 2.8 (1.22) | 2.7 (0.99) |
| run-505 | 2.8 (1.76) | 2.8 (1.34) | 2.8 (1.41) | 2.8 (1.08) | 2.7 (0.83) |
| run-506 | 2.4 (1.48) | 2.3 (1.07) | 2.3 (1.13) | 2.2 (0.83) | 2.2 (0.61) |
| run-507 | 2.4 (1.42) | 2.2 (0.95) | 2.3 (1.02) | 2.2 (0.70) | 2.1 (0.48) |
| run-508 | 1.8 (1.25) | 1.7 (0.88) | 1.7 (0.93) | 1.7 (0.65) | 1.6 (0.47) |
