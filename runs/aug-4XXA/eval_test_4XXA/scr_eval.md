# SCR anchors: aug-4XXA on test_4XXA

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 3.7 / 9.1 | 0.39 / 0.50 | 2416 | 11 |
| run-402 | 37 | 100 % | 5.8 / 9.2 | 0.54 / 0.65 | 2513 | 11 |
| run-403 | 59 | 100 % | 6.5 / 9.1 | 0.61 / 0.93 | 2430 | 11 |
| run-404 | 39 | 100 % | 8.1 / 11.9 | 0.85 / 1.02 | 2243 | 14 |
| run-405 | 38 | 100 % | 6.2 / 12.2 | 0.53 / 0.73 | 2132 | 15 |
| run-406 | 39 | 100 % | 5.9 / 10.9 | 0.36 / 0.51 | 2281 | 14 |
| run-407 | 39 | 100 % | 5.1 / 6.8 | 0.44 / 0.60 | 2577 | 10 |
| run-408 | 39 | 100 % | 7.7 / 16.6 | 0.48 / 0.75 | 2167 | 15 |
| **all (pooled)** | 348 | 100 % | 5.8 / 10.8 | 0.48 / 0.85 | 2331 | 12 |
| **mean of sweep medians** | | | 6.1 | | | |
