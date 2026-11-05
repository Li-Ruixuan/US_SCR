# Single-model tracking: SCR alone on every 2th row (train_2XX, `runs/v2map-2XX-owncalib/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-2XX-owncalib/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **5.48** | 21.99 | 100 % | 2.455 | 3.85 |
| smoothed 0.25 s | **5.27** | 21.52 | 100 % | 1.199 | 3.22 |
| smoothed 0.5 s | **5.28** | 21.23 | 100 % | 1.189 | 3.30 |
| smoothed 1 s | **5.24** | 21.68 | 100 % | 0.827 | 2.89 |
| smoothed 2 s | **5.21** | 21.94 | 100 % | 0.717 | 2.55 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-205 | 7.5 (5.52) | 7.3 (4.89) | 7.3 (4.99) | 7.3 (4.61) | 7.2 (4.21) |
| run-211 | 3.4 (2.17) | 3.2 (1.54) | 3.2 (1.61) | 3.2 (1.17) | 3.2 (0.89) |
