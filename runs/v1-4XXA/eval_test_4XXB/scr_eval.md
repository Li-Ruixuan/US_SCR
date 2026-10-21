# SCR anchors: v1-4XXA on test_4XXB

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 20.8 / 28.3 | 0.76 / 0.99 | 1762 | 32 |
| run-410 | 38 | 100 % | 29.4 / 44.6 | 1.07 / 1.56 | 1405 | 87 |
| run-411 | 38 | 100 % | 39.5 / 59.0 | 1.48 / 1.96 | 1708 | 36 |
| run-412 | 39 | 100 % | 37.0 / 48.3 | 1.51 / 1.81 | 1237 | 161 |
| **all (pooled)** | 155 | 100 % | 31.2 / 47.3 | 1.17 / 1.72 | 1497 | 65 |
| **mean of sweep medians** | | | 31.7 | | | |
