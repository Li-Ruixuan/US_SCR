# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-exam-e40/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.46** | 4.75 | 100 % | 1.266 | 1.51 |
| smoothed 0.25 s | **2.37** | 4.56 | 100 % | 0.517 | 1.10 |
| smoothed 0.5 s | **2.36** | 4.57 | 100 % | 0.524 | 1.15 |
| smoothed 1 s | **2.34** | 4.52 | 100 % | 0.288 | 0.85 |
| smoothed 2 s | **2.31** | 4.47 | 100 % | 0.226 | 0.65 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 2.3 (1.42) | 2.2 (1.02) | 2.2 (1.08) | 2.1 (0.79) | 2.1 (0.56) |
| run-502 | 2.1 (1.31) | 2.0 (0.96) | 2.0 (1.01) | 2.0 (0.77) | 2.0 (0.65) |
| run-503 | 2.6 (1.41) | 2.5 (1.05) | 2.5 (1.11) | 2.4 (0.82) | 2.4 (0.61) |
| run-504 | 3.1 (1.96) | 3.0 (1.44) | 3.0 (1.49) | 2.9 (1.15) | 3.0 (0.95) |
| run-505 | 3.0 (1.75) | 3.0 (1.32) | 3.0 (1.39) | 3.0 (1.05) | 2.9 (0.83) |
| run-506 | 2.4 (1.53) | 2.2 (1.09) | 2.2 (1.15) | 2.2 (0.83) | 2.2 (0.60) |
| run-507 | 2.4 (1.45) | 2.4 (0.97) | 2.3 (1.04) | 2.4 (0.71) | 2.3 (0.49) |
| run-508 | 1.8 (1.27) | 1.7 (0.91) | 1.7 (0.96) | 1.6 (0.67) | 1.6 (0.47) |
