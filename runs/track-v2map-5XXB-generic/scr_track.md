# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXB-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-generic/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.41** | 7.53 | 100 % | 0.978 | 1.26 |
| smoothed 0.25 s | **3.36** | 7.46 | 100 % | 0.440 | 0.98 |
| smoothed 0.5 s | **3.37** | 7.47 | 100 % | 0.442 | 1.02 |
| smoothed 1 s | **3.36** | 7.44 | 100 % | 0.273 | 0.81 |
| smoothed 2 s | **3.35** | 7.41 | 100 % | 0.233 | 0.68 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | 4.3 (1.26) | 4.3 (0.97) | 4.3 (1.01) | 4.3 (0.79) | 4.3 (0.68) |
| run-510 | 2.6 (1.22) | 2.5 (0.88) | 2.5 (0.92) | 2.5 (0.70) | 2.5 (0.54) |
| run-511 | 2.7 (1.00) | 2.7 (0.69) | 2.7 (0.73) | 2.7 (0.53) | 2.7 (0.41) |
| run-512 | 3.4 (1.33) | 3.3 (1.00) | 3.3 (1.03) | 3.3 (0.80) | 3.2 (0.63) |
| run-513 | 3.5 (1.27) | 3.4 (0.97) | 3.5 (1.02) | 3.5 (0.78) | 3.4 (0.60) |
| run-514 | 3.5 (1.57) | 3.5 (1.30) | 3.5 (1.36) | 3.5 (1.13) | 3.5 (1.01) |
| run-515 | 3.7 (1.08) | 3.7 (0.89) | 3.7 (0.92) | 3.8 (0.79) | 3.7 (0.71) |
| run-516 | 3.5 (1.36) | 3.5 (1.11) | 3.5 (1.16) | 3.5 (0.96) | 3.5 (0.81) |
