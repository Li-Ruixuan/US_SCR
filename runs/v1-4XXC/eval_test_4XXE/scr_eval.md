# SCR anchors: v1-4XXC on test_4XXE

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-425 | 39 | 100 % | 10.7 / 14.0 | 0.62 / 0.89 | 2145 | 15 |
| run-426 | 39 | 100 % | 7.3 / 11.5 | 0.45 / 0.60 | 2190 | 14 |
| run-427 | 39 | 100 % | 17.7 / 54.4 | 0.99 / 2.21 | 1363 | 101 |
| run-428 | 38 | 100 % | 4.9 / 11.5 | 0.48 / 0.66 | 2510 | 10 |
| **all (pooled)** | 155 | 100 % | 10.4 / 20.5 | 0.56 / 1.17 | 2056 | 17 |
| **mean of sweep medians** | | | 10.2 | | | |
