# Single-model tracking: SCR alone on every 2th row (test_5XXC, `runs/v2map-5XXA-exam/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-exam/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **14.82** | 48.55 | 5 % | 16.354 | 17.87 |
| smoothed 0.25 s | **60.25** | 89.35 | 21 % | 2.351 | 4.93 |
| smoothed 0.5 s | **60.56** | 89.35 | 21 % | 2.398 | 5.08 |
| smoothed 1 s | **59.41** | 89.35 | 21 % | 1.674 | 4.12 |
| smoothed 2 s | **58.72** | 89.35 | 21 % | 1.443 | 3.52 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-517 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-518 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-519 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-520 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-521 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-522 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-523 | 12.9 (9.01) | 34.0 (5.73) | 34.0 (5.85) | 33.8 (4.91) | 32.5 (4.46) |
| run-524 | 16.8 (26.74) | 86.5 (4.12) | 87.2 (4.31) | 85.0 (3.33) | 85.0 (2.58) |
