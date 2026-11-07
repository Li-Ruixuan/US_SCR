# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXA-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **4.48** | 8.68 | 100 % | 2.092 | 2.42 |
| smoothed 0.25 s | **4.32** | 8.44 | 100 % | 0.815 | 1.70 |
| smoothed 0.5 s | **4.33** | 8.47 | 100 % | 0.815 | 1.80 |
| smoothed 1 s | **4.28** | 8.37 | 100 % | 0.419 | 1.32 |
| smoothed 2 s | **4.23** | 8.25 | 100 % | 0.289 | 0.92 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | 4.7 (2.58) | 4.8 (1.79) | 4.7 (1.88) | 4.8 (1.34) | 4.7 (0.92) |
| run-510 | 3.6 (2.39) | 3.4 (1.57) | 3.4 (1.66) | 3.4 (1.14) | 3.3 (0.73) |
| run-511 | 2.9 (2.39) | 2.7 (1.54) | 2.7 (1.65) | 2.7 (1.07) | 2.7 (0.63) |
| run-512 | 7.4 (2.02) | 7.2 (1.42) | 7.3 (1.51) | 7.2 (1.08) | 7.2 (0.74) |
| run-513 | 3.7 (2.54) | 3.5 (1.79) | 3.6 (1.87) | 3.4 (1.39) | 3.3 (0.94) |
| run-514 | 4.3 (2.75) | 4.1 (2.17) | 4.1 (2.27) | 4.0 (1.82) | 4.0 (1.44) |
| run-515 | 5.1 (1.99) | 4.9 (1.43) | 4.9 (1.51) | 4.8 (1.13) | 4.8 (0.84) |
| run-516 | 4.2 (2.69) | 3.9 (1.93) | 3.9 (2.03) | 3.9 (1.59) | 3.9 (1.16) |
