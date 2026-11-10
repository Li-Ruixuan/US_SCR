# Single-model tracking: SCR alone on every 2th row (test_5XXE, `runs/v2map-5XXE-exam-seed1/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXE-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **6.35** | 9.94 | 100 % | 0.717 | 1.01 |
| smoothed 0.25 s | **6.33** | 9.87 | 100 % | 0.365 | 0.84 |
| smoothed 0.5 s | **6.34** | 9.89 | 100 % | 0.373 | 0.88 |
| smoothed 1 s | **6.31** | 9.89 | 100 % | 0.243 | 0.73 |
| smoothed 2 s | **6.29** | 9.88 | 100 % | 0.219 | 0.65 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-529 | 5.7 (0.96) | 5.6 (0.78) | 5.6 (0.81) | 5.6 (0.66) | 5.5 (0.55) |
| run-530 | 5.9 (0.85) | 5.9 (0.66) | 5.9 (0.69) | 5.9 (0.56) | 5.9 (0.48) |
| run-531 | 8.3 (1.17) | 8.3 (1.08) | 8.3 (1.12) | 8.3 (0.98) | 8.3 (0.96) |
| run-532 | 5.6 (1.06) | 5.5 (0.86) | 5.5 (0.89) | 5.5 (0.71) | 5.5 (0.61) |
