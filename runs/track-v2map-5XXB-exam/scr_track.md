# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXB-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **4.46** | 7.61 | 100 % | 1.060 | 1.35 |
| smoothed 0.25 s | **4.43** | 7.55 | 100 % | 0.467 | 1.04 |
| smoothed 0.5 s | **4.43** | 7.55 | 100 % | 0.473 | 1.09 |
| smoothed 1 s | **4.43** | 7.52 | 100 % | 0.287 | 0.86 |
| smoothed 2 s | **4.41** | 7.51 | 100 % | 0.239 | 0.70 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | 4.4 (1.29) | 4.3 (0.99) | 4.3 (1.03) | 4.3 (0.81) | 4.3 (0.69) |
| run-510 | 4.5 (1.26) | 4.5 (0.92) | 4.5 (0.96) | 4.5 (0.73) | 4.4 (0.56) |
| run-511 | 3.2 (1.11) | 3.1 (0.78) | 3.1 (0.83) | 3.1 (0.59) | 3.1 (0.46) |
| run-512 | 6.3 (1.64) | 6.3 (1.17) | 6.3 (1.23) | 6.3 (0.90) | 6.3 (0.69) |
| run-513 | 3.9 (1.36) | 3.9 (1.05) | 3.9 (1.10) | 3.9 (0.84) | 3.9 (0.63) |
| run-514 | 4.6 (1.57) | 4.5 (1.32) | 4.5 (1.37) | 4.5 (1.15) | 4.5 (1.01) |
| run-515 | 4.8 (1.14) | 4.7 (0.94) | 4.7 (0.98) | 4.7 (0.84) | 4.7 (0.75) |
| run-516 | 4.1 (1.46) | 4.1 (1.17) | 4.1 (1.22) | 4.1 (1.00) | 4.1 (0.84) |
