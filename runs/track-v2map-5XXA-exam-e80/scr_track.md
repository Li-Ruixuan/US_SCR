# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-exam-e80/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.50** | 4.87 | 100 % | 1.251 | 1.51 |
| smoothed 0.25 s | **2.40** | 4.70 | 100 % | 0.514 | 1.09 |
| smoothed 0.5 s | **2.41** | 4.72 | 100 % | 0.520 | 1.15 |
| smoothed 1 s | **2.37** | 4.68 | 100 % | 0.289 | 0.85 |
| smoothed 2 s | **2.34** | 4.65 | 100 % | 0.227 | 0.65 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.5 (1.44) | 2.4 (1.04) | 2.4 (1.10) | 2.4 (0.81) | 2.4 (0.56) |
| run-502 | 2.0 (1.28) | 2.0 (0.93) | 2.0 (0.98) | 2.0 (0.74) | 2.0 (0.63) |
| run-503 | 2.5 (1.40) | 2.3 (1.03) | 2.4 (1.09) | 2.3 (0.82) | 2.4 (0.63) |
| run-504 | 3.0 (1.97) | 2.9 (1.45) | 2.9 (1.51) | 2.8 (1.17) | 2.8 (0.96) |
| run-505 | 3.1 (1.78) | 3.0 (1.35) | 3.0 (1.42) | 3.0 (1.07) | 2.9 (0.84) |
| run-506 | 2.5 (1.50) | 2.4 (1.09) | 2.4 (1.15) | 2.4 (0.84) | 2.4 (0.61) |
| run-507 | 2.5 (1.43) | 2.4 (0.95) | 2.4 (1.02) | 2.4 (0.70) | 2.2 (0.48) |
| run-508 | 1.9 (1.27) | 1.7 (0.90) | 1.7 (0.95) | 1.7 (0.67) | 1.6 (0.47) |
