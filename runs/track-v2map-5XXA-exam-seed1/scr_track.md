# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-exam-seed1/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.42** | 5.03 | 100 % | 1.246 | 1.51 |
| smoothed 0.25 s | **2.29** | 4.88 | 100 % | 0.511 | 1.09 |
| smoothed 0.5 s | **2.30** | 4.90 | 100 % | 0.518 | 1.15 |
| smoothed 1 s | **2.25** | 4.85 | 100 % | 0.289 | 0.85 |
| smoothed 2 s | **2.24** | 4.80 | 100 % | 0.226 | 0.65 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.5 (1.41) | 2.4 (1.00) | 2.4 (1.06) | 2.4 (0.78) | 2.4 (0.54) |
| run-502 | 1.9 (1.28) | 1.8 (0.94) | 1.8 (0.99) | 1.8 (0.76) | 1.8 (0.64) |
| run-503 | 2.5 (1.39) | 2.4 (1.02) | 2.4 (1.08) | 2.4 (0.81) | 2.4 (0.62) |
| run-504 | 2.9 (2.00) | 2.7 (1.48) | 2.7 (1.54) | 2.6 (1.20) | 2.6 (0.97) |
| run-505 | 3.0 (1.80) | 2.9 (1.37) | 2.9 (1.44) | 2.9 (1.09) | 2.8 (0.84) |
| run-506 | 2.5 (1.47) | 2.4 (1.07) | 2.4 (1.12) | 2.4 (0.83) | 2.3 (0.61) |
| run-507 | 2.4 (1.43) | 2.2 (0.96) | 2.2 (1.02) | 2.1 (0.71) | 2.0 (0.50) |
| run-508 | 1.7 (1.27) | 1.6 (0.90) | 1.6 (0.95) | 1.5 (0.66) | 1.5 (0.47) |
