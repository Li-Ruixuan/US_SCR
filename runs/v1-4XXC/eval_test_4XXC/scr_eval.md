# SCR anchors: v1-4XXC on test_4XXC

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 8.7 / 12.4 | 0.83 / 1.05 | 2363 | 12 |
| run-414 | 39 | 100 % | 14.3 / 19.4 | 1.15 / 1.36 | 1537 | 58 |
| run-415 | 39 | 100 % | 11.0 / 16.3 | 0.98 / 1.36 | 1882 | 24 |
| run-416 | 39 | 100 % | 10.8 / 17.1 | 0.94 / 1.28 | 1919 | 23 |
| **all (pooled)** | 155 | 100 % | 11.0 / 17.0 | 0.96 / 1.33 | 1923 | 23 |
| **mean of sweep medians** | | | 11.2 | | | |
