# Single-model tracking: SCR alone on every 2th row (test_5XXD, `runs/v2map-5XXC-exam-seed1/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXC-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **2.25** | 3.99 | 100 % | 0.947 | 1.28 |
| smoothed 0.25 s | **2.21** | 3.86 | 100 % | 0.466 | 1.02 |
| smoothed 0.5 s | **2.21** | 3.85 | 100 % | 0.479 | 1.07 |
| smoothed 1 s | **2.18** | 3.78 | 100 % | 0.296 | 0.82 |
| smoothed 2 s | **2.16** | 3.72 | 100 % | 0.265 | 0.71 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-525 | 2.4 (1.32) | 2.3 (1.00) | 2.4 (1.06) | 2.3 (0.78) | 2.3 (0.61) |
| run-526 | 2.0 (1.19) | 2.0 (0.93) | 2.0 (0.98) | 2.0 (0.74) | 1.9 (0.63) |
| run-527 | 2.1 (1.34) | 2.0 (1.09) | 2.0 (1.14) | 2.0 (0.88) | 1.9 (0.83) |
| run-528 | 2.5 (1.29) | 2.5 (1.05) | 2.5 (1.10) | 2.4 (0.86) | 2.4 (0.78) |
