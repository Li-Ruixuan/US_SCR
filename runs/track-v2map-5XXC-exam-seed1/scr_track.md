# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXC-exam-seed1/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.11** | 5.13 | 100 % | 0.627 | 0.80 |
| smoothed 0.25 s | **3.11** | 5.07 | 100 % | 0.293 | 0.61 |
| smoothed 0.5 s | **3.11** | 5.11 | 100 % | 0.295 | 0.64 |
| smoothed 1 s | **3.09** | 5.06 | 100 % | 0.189 | 0.51 |
| smoothed 2 s | **3.06** | 4.97 | 100 % | 0.170 | 0.44 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | 3.7 (0.62) | 3.6 (0.47) | 3.6 (0.49) | 3.7 (0.38) | 3.6 (0.36) |
| run-518 | 2.5 (0.56) | 2.5 (0.41) | 2.5 (0.44) | 2.5 (0.33) | 2.5 (0.27) |
| run-519 | 2.5 (0.61) | 2.5 (0.47) | 2.5 (0.49) | 2.6 (0.40) | 2.6 (0.36) |
| run-520 | 5.1 (0.93) | 5.2 (0.75) | 5.2 (0.78) | 5.1 (0.64) | 4.9 (0.58) |
| run-521 | 2.6 (0.69) | 2.6 (0.53) | 2.6 (0.55) | 2.6 (0.44) | 2.6 (0.38) |
| run-522 | 2.0 (0.64) | 2.0 (0.50) | 2.0 (0.51) | 2.0 (0.42) | 2.0 (0.38) |
| run-523 | 3.5 (1.37) | 3.5 (1.09) | 3.5 (1.15) | 3.5 (0.90) | 3.5 (0.75) |
| run-524 | 2.9 (0.95) | 2.8 (0.70) | 2.9 (0.74) | 2.8 (0.57) | 2.8 (0.45) |
