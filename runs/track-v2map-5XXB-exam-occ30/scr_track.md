# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXB-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.22** | 9.21 | 100 % | 1.256 | 1.69 |
| smoothed 0.25 s | **5.18** | 9.15 | 100 % | 0.568 | 1.34 |
| smoothed 0.5 s | **5.17** | 9.17 | 100 % | 0.572 | 1.39 |
| smoothed 1 s | **5.16** | 9.11 | 100 % | 0.362 | 1.14 |
| smoothed 2 s | **5.15** | 9.00 | 100 % | 0.308 | 0.96 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | 4.7 (1.58) | 4.6 (1.24) | 4.7 (1.29) | 4.6 (1.06) | 4.7 (0.90) |
| run-510 | 5.5 (1.65) | 5.5 (1.24) | 5.5 (1.29) | 5.6 (1.02) | 5.5 (0.84) |
| run-511 | 3.7 (1.52) | 3.6 (1.13) | 3.6 (1.18) | 3.6 (0.94) | 3.7 (0.75) |
| run-512 | 7.5 (2.11) | 7.6 (1.66) | 7.6 (1.73) | 7.5 (1.35) | 7.5 (1.23) |
| run-513 | 4.3 (1.68) | 4.2 (1.31) | 4.2 (1.37) | 4.2 (1.08) | 4.2 (0.81) |
| run-514 | 5.3 (1.83) | 5.2 (1.53) | 5.2 (1.59) | 5.2 (1.35) | 5.2 (1.16) |
| run-515 | 5.6 (1.41) | 5.6 (1.19) | 5.6 (1.24) | 5.5 (1.08) | 5.6 (0.95) |
| run-516 | 5.1 (1.75) | 5.0 (1.42) | 5.0 (1.48) | 5.0 (1.24) | 5.0 (1.05) |
