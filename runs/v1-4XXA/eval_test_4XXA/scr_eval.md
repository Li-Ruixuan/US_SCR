# SCR anchors: v1-4XXA on test_4XXA

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 6.8 / 11.3 | 0.43 / 0.71 | 2408 | 11 |
| run-402 | 37 | 100 % | 8.6 / 12.2 | 0.61 / 0.91 | 2546 | 11 |
| run-403 | 59 | 100 % | 8.5 / 10.7 | 0.62 / 0.83 | 2532 | 10 |
| run-404 | 39 | 100 % | 17.3 / 26.2 | 1.02 / 1.53 | 2246 | 14 |
| run-405 | 38 | 100 % | 12.4 / 21.7 | 0.72 / 1.16 | 2206 | 14 |
| run-406 | 39 | 100 % | 7.4 / 12.5 | 0.44 / 0.57 | 2370 | 12 |
| run-407 | 39 | 100 % | 7.4 / 13.3 | 0.55 / 0.83 | 2436 | 11 |
| run-408 | 39 | 100 % | 10.8 / 18.1 | 0.69 / 0.95 | 2152 | 16 |
| **all (pooled)** | 348 | 100 % | 8.9 / 17.6 | 0.60 / 1.00 | 2364 | 12 |
| **mean of sweep medians** | | | 9.9 | | | |
