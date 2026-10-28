# Single-model tracking: SCR alone on every 2th row (train_2XX, `runs/bigclean-2XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.59** | 7.46 | 100 % | 2.302 | 2.72 |
| smoothed 0.25 s | **3.36** | 7.06 | 100 % | 0.948 | 1.96 |
| smoothed 0.5 s | **3.40** | 7.13 | 100 % | 0.925 | 2.03 |
| smoothed 1 s | **3.39** | 7.05 | 100 % | 0.501 | 1.56 |
| smoothed 2 s | **3.35** | 6.85 | 100 % | 0.392 | 1.20 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-205 | 4.0 (3.26) | 3.8 (2.39) | 3.9 (2.46) | 3.9 (1.94) | 3.8 (1.53) |
| run-211 | 3.2 (2.17) | 2.9 (1.53) | 2.9 (1.60) | 2.9 (1.17) | 2.9 (0.88) |
