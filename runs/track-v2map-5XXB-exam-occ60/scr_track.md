# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXB-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.07** | 11.45 | 87 % | 1.823 | 2.34 |
| smoothed 0.25 s | **5.29** | 11.55 | 100 % | 0.985 | 2.21 |
| smoothed 0.5 s | **5.29** | 11.53 | 100 % | 0.970 | 2.24 |
| smoothed 1 s | **5.28** | 11.21 | 100 % | 0.691 | 1.88 |
| smoothed 2 s | **5.25** | 10.92 | 100 % | 0.594 | 1.60 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | 4.6 (2.40) | 4.6 (2.11) | 4.6 (2.13) | 4.6 (1.74) | 4.6 (1.50) |
| run-510 | 5.0 (1.72) | 5.4 (1.87) | 5.4 (1.90) | 5.4 (1.67) | 5.3 (1.52) |
| run-511 | 3.4 (1.97) | 3.5 (1.84) | 3.6 (1.87) | 3.5 (1.53) | 3.5 (1.29) |
| run-512 | 7.8 (3.14) | 8.5 (2.80) | 8.5 (2.84) | 8.5 (2.33) | 8.4 (1.86) |
| run-513 | 4.2 (2.10) | 4.2 (1.85) | 4.3 (1.86) | 4.3 (1.55) | 4.3 (1.33) |
| run-514 | 5.0 (2.36) | 5.3 (2.42) | 5.3 (2.49) | 5.3 (2.20) | 5.3 (1.89) |
| run-515 | 5.3 (2.07) | 5.6 (1.99) | 5.6 (1.96) | 5.6 (1.69) | 5.6 (1.42) |
| run-516 | 5.2 (2.95) | 5.2 (2.81) | 5.2 (2.89) | 5.2 (2.34) | 5.1 (1.94) |
