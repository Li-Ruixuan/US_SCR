# Single-model tracking: SCR alone on every 2th row (test_5XXB, `runs/v2map-5XXB-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXB-generic/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **nan** | nan | 0 % | nan | nan |
| smoothed 0.25 s | **nan** | nan | 0 % | nan | nan |
| smoothed 0.5 s | **nan** | nan | 0 % | nan | nan |
| smoothed 1 s | **nan** | nan | 0 % | nan | nan |
| smoothed 2 s | **nan** | nan | 0 % | nan | nan |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-509 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-510 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-511 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-512 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-513 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-514 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-515 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
| run-516 | nan (nan) | nan (nan) | nan (nan) | nan (nan) | nan (nan) |
