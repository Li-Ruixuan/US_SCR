# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.43** | 4.98 | 100 % | 1.245 | 1.50 |
| smoothed 0.25 s | **2.33** | 4.82 | 100 % | 0.510 | 1.09 |
| smoothed 0.5 s | **2.34** | 4.83 | 100 % | 0.516 | 1.15 |
| smoothed 1 s | **2.28** | 4.77 | 100 % | 0.289 | 0.85 |
| smoothed 2 s | **2.26** | 4.75 | 100 % | 0.228 | 0.65 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.4 (1.42) | 2.3 (1.02) | 2.3 (1.08) | 2.3 (0.80) | 2.2 (0.55) |
| run-502 | 2.0 (1.25) | 2.0 (0.92) | 2.0 (0.97) | 2.0 (0.74) | 2.0 (0.64) |
| run-503 | 2.4 (1.43) | 2.3 (1.06) | 2.3 (1.11) | 2.2 (0.83) | 2.2 (0.63) |
| run-504 | 2.9 (1.96) | 2.8 (1.44) | 2.9 (1.50) | 2.8 (1.17) | 2.7 (0.97) |
| run-505 | 3.0 (1.78) | 2.8 (1.35) | 2.8 (1.42) | 2.8 (1.07) | 2.8 (0.85) |
| run-506 | 2.4 (1.47) | 2.4 (1.07) | 2.4 (1.12) | 2.3 (0.83) | 2.3 (0.60) |
| run-507 | 2.5 (1.43) | 2.3 (0.94) | 2.3 (1.01) | 2.2 (0.69) | 2.2 (0.48) |
| run-508 | 1.8 (1.26) | 1.7 (0.90) | 1.7 (0.95) | 1.7 (0.66) | 1.6 (0.47) |
