# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXC-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.91** | 11.00 | 98 % | 1.803 | 2.28 |
| smoothed 0.25 s | **3.90** | 11.11 | 100 % | 0.814 | 1.80 |
| smoothed 0.5 s | **3.89** | 11.07 | 100 % | 0.798 | 1.82 |
| smoothed 1 s | **3.89** | 10.69 | 100 % | 0.466 | 1.41 |
| smoothed 2 s | **3.86** | 10.34 | 100 % | 0.347 | 1.09 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | 4.7 (2.60) | 4.7 (1.92) | 4.7 (1.99) | 4.6 (1.52) | 4.6 (1.13) |
| run-518 | 3.1 (1.72) | 3.1 (1.33) | 3.1 (1.38) | 3.1 (1.07) | 3.1 (0.81) |
| run-519 | 3.2 (2.33) | 3.2 (1.86) | 3.2 (1.77) | 3.2 (1.36) | 3.2 (1.10) |
| run-520 | 6.7 (2.86) | 6.6 (2.19) | 6.6 (2.25) | 6.6 (1.74) | 6.6 (1.27) |
| run-521 | 3.2 (1.93) | 3.2 (1.51) | 3.2 (1.54) | 3.2 (1.17) | 3.2 (0.96) |
| run-522 | 2.7 (1.89) | 2.6 (1.38) | 2.6 (1.41) | 2.6 (1.11) | 2.7 (0.80) |
| run-523 | 4.5 (3.28) | 4.5 (2.55) | 4.5 (2.57) | 4.4 (1.96) | 4.3 (1.45) |
| run-524 | 3.3 (1.65) | 3.3 (1.62) | 3.3 (1.64) | 3.3 (1.35) | 3.3 (1.22) |
