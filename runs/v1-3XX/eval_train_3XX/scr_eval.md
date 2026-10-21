# SCR anchors: v1-3XX on train_3XX

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 2.5 / 3.8 | 0.20 / 0.47 | 3511 | 7 |
| run-314 | 29 | 100 % | 3.7 / 5.9 | 0.14 / 0.24 | 3518 | 8 |
| run-315 | 29 | 100 % | 2.3 / 5.8 | 0.29 / 0.52 | 3512 | 8 |
| run-316 | 30 | 100 % | 1.7 / 3.1 | 0.12 / 0.24 | 3530 | 7 |
| run-317 | 23 | 100 % | 2.3 / 7.7 | 0.23 / 0.40 | 3491 | 8 |
| **all (pooled)** | 140 | 100 % | 2.3 / 5.4 | 0.18 / 0.42 | 3512 | 8 |
| **mean of sweep medians** | | | 2.5 | | | |
