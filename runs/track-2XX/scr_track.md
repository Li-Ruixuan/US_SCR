# Single-model tracking: SCR alone on every 2th row (train_2XX, `runs/bigclean-2XX/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **3.59** | 7.46 | 100 % | 2.302 | 2.72 |
| smoothed 0.25 s | **3.36** | 7.06 | 100 % | 0.948 | 1.96 |
| smoothed 0.5 s | **3.40** | 7.13 | 100 % | 0.925 | 2.03 |
| smoothed 1 s | **3.39** | 7.05 | 100 % | 0.501 | 1.56 |
| smoothed 2 s | **3.35** | 6.85 | 100 % | 0.392 | 1.20 |
| real time 0.25 s, delay 0 s | **3.26** | 7.08 | 100 % | 0.845 | 1.82 |
| real time 0.5 s, delay 0 s | **3.44** | 7.27 | 100 % | 1.168 | 2.33 |
| real time 1 s, delay 0 s | **3.44** | 7.31 | 100 % | 0.748 | 1.89 |
| real time 2 s, delay 0 s | **3.54** | 7.46 | 100 % | 0.546 | 1.59 |
| real time 0.25 s, delay 0.25 s | **3.61** | 7.24 | 100 % | 0.908 | 2.01 |
| real time 0.5 s, delay 0.25 s | **3.33** | 6.95 | 100 % | 0.493 | 1.34 |
| real time 1 s, delay 0.25 s | **3.32** | 6.89 | 100 % | 0.489 | 1.30 |
| real time 2 s, delay 0.25 s | **3.37** | 6.74 | 100 % | 0.430 | 1.19 |
| real time 0.25 s, delay 0.5 s | **5.21** | 9.43 | 100 % | 1.509 | 2.80 |
| real time 0.5 s, delay 0.5 s | **3.43** | 7.27 | 100 % | 1.208 | 2.41 |
| real time 1 s, delay 0.5 s | **3.31** | 6.66 | 100 % | 0.386 | 1.13 |
| real time 2 s, delay 0.5 s | **3.30** | 6.65 | 100 % | 0.393 | 1.15 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s | real time 0.25 s, delay 0 s | real time 0.5 s, delay 0 s | real time 1 s, delay 0 s | real time 2 s, delay 0 s | real time 0.25 s, delay 0.25 s | real time 0.5 s, delay 0.25 s | real time 1 s, delay 0.25 s | real time 2 s, delay 0.25 s | real time 0.25 s, delay 0.5 s | real time 0.5 s, delay 0.5 s | real time 1 s, delay 0.5 s | real time 2 s, delay 0.5 s |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| run-205 | 4.0 (3.26) | 3.8 (2.39) | 3.9 (2.46) | 3.9 (1.94) | 3.8 (1.53) | 3.5 (2.21) | 3.9 (2.81) | 3.9 (2.34) | 4.1 (2.07) | 4.3 (2.48) | 3.7 (1.68) | 3.7 (1.63) | 3.8 (1.52) | 7.1 (3.54) | 3.9 (2.92) | 3.7 (1.41) | 3.7 (1.43) |
| run-211 | 3.2 (2.17) | 2.9 (1.53) | 2.9 (1.60) | 2.9 (1.17) | 2.9 (0.88) | 3.0 (1.43) | 3.0 (1.85) | 3.0 (1.45) | 3.0 (1.12) | 2.9 (1.55) | 2.9 (0.99) | 2.9 (0.96) | 2.9 (0.86) | 3.4 (2.06) | 3.0 (1.91) | 2.9 (0.84) | 2.9 (0.87) |
