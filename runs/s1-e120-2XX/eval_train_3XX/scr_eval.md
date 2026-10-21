# SCR anchors: s1-e120-2XX on train_3XX

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 13.9 / 48.8 | 0.70 / 1.62 | 1751 | 38 |
| run-314 | 29 | 100 % | 26.1 / 48.2 | 0.90 / 1.57 | 2516 | 11 |
| run-315 | 29 | 100 % | 13.5 / 20.8 | 0.50 / 0.94 | 1963 | 21 |
| run-316 | 30 | 100 % | 24.2 / 46.3 | 0.82 / 1.37 | 1921 | 23 |
| run-317 | 23 | 100 % | 28.2 / 56.5 | 0.79 / 1.56 | 1589 | 49 |
| **all (pooled)** | 140 | 100 % | 22.3 / 47.8 | 0.70 / 1.46 | 1856 | 26 |
| **mean of sweep medians** | | | 21.2 | | | |
