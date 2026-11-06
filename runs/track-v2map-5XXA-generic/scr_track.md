# Single-model tracking: SCR alone on every 2th row (test_5XXA, `runs/v2map-5XXA-generic/best.pt`)

No odometry, no Polaris start pose; Kabsch RANSAC, gate >= 400 inliers; camera calibration from `/data2/u0137815/US_SCR/runs/map-5XXA-generic/map.json`. Error at the US image (5 points, mm): median per sweep, mean over sweeps; step-to-step error = mean change of the error vector between rows (2 row(s), 66 ms) and 8 rows (anchoring.py's odometry step).

| method | US image median | p90 | frames with a pose | step, 2 row(s) | step, 8 rows |
|---|---|---|---|---|---|
| raw | **13.62** | 19.36 | 100 % | 1.803 | 2.14 |
| smoothed 0.25 s | **13.57** | 19.19 | 100 % | 0.715 | 1.56 |
| smoothed 0.5 s | **13.59** | 19.19 | 100 % | 0.718 | 1.63 |
| smoothed 1 s | **13.57** | 19.15 | 100 % | 0.392 | 1.24 |
| smoothed 2 s | **13.57** | 19.14 | 100 % | 0.296 | 0.95 |

Per sweep (US image median, step 8 rows):

| sweep | raw | smoothed 0.25 s | smoothed 0.5 s | smoothed 1 s | smoothed 2 s |
|---|---|---|---|---|---|
| run-501 | 13.5 (1.75) | 13.5 (1.26) | 13.5 (1.33) | 13.5 (0.98) | 13.5 (0.73) |
| run-502 | 15.4 (1.71) | 15.4 (1.26) | 15.4 (1.32) | 15.4 (1.02) | 15.4 (0.82) |
| run-503 | 16.4 (2.77) | 16.3 (2.04) | 16.3 (2.14) | 16.3 (1.62) | 16.3 (1.11) |
| run-504 | 10.1 (2.56) | 9.8 (1.91) | 9.9 (1.98) | 9.8 (1.57) | 9.8 (1.31) |
| run-505 | 12.5 (2.79) | 12.4 (2.16) | 12.5 (2.24) | 12.4 (1.82) | 12.4 (1.49) |
| run-506 | 12.0 (1.88) | 12.0 (1.35) | 12.0 (1.42) | 12.0 (1.08) | 11.9 (0.81) |
| run-507 | 15.3 (2.08) | 15.3 (1.38) | 15.3 (1.47) | 15.4 (1.03) | 15.4 (0.71) |
| run-508 | 13.9 (1.58) | 13.9 (1.10) | 13.9 (1.17) | 13.9 (0.84) | 13.9 (0.61) |
