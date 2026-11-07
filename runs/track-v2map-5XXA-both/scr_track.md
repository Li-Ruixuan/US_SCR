# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-both/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-both/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.28** | 5.35 | 100 % | 1.224 | 1.47 |
| smoothed 0.25 s | **3.17** | 5.21 | 100 % | 0.500 | 1.07 |
| smoothed 0.5 s | **3.18** | 5.21 | 100 % | 0.507 | 1.12 |
| smoothed 1 s | **3.15** | 5.20 | 100 % | 0.284 | 0.83 |
| smoothed 2 s | **3.11** | 5.15 | 100 % | 0.224 | 0.64 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 3.4 (1.35) | 3.3 (0.97) | 3.3 (1.03) | 3.3 (0.76) | 3.2 (0.56) |
| run-502 | 2.8 (1.24) | 2.7 (0.90) | 2.7 (0.95) | 2.7 (0.73) | 2.7 (0.61) |
| run-503 | 3.6 (1.38) | 3.5 (1.03) | 3.5 (1.08) | 3.5 (0.80) | 3.5 (0.59) |
| run-504 | 3.5 (1.90) | 3.3 (1.40) | 3.3 (1.46) | 3.3 (1.14) | 3.2 (0.95) |
| run-505 | 3.8 (1.78) | 3.7 (1.36) | 3.7 (1.42) | 3.7 (1.10) | 3.7 (0.87) |
| run-506 | 3.4 (1.46) | 3.3 (1.05) | 3.3 (1.11) | 3.3 (0.81) | 3.2 (0.60) |
| run-507 | 3.1 (1.40) | 3.0 (0.92) | 3.0 (0.98) | 2.9 (0.66) | 2.9 (0.47) |
| run-508 | 2.6 (1.25) | 2.6 (0.88) | 2.6 (0.94) | 2.5 (0.66) | 2.5 (0.47) |
