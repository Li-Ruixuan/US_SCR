# SCR anchors: scr-3XX on train_3XX

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 10.5 / 22.4 | 0.49 / 0.81 | 1663 | 50 |
| run-314 | 29 | 100 % | 10.4 / 23.2 | 0.40 / 0.72 | 1812 | 28 |
| run-315 | 29 | 100 % | 13.0 / 24.3 | 0.66 / 1.05 | 1746 | 33 |
| run-316 | 30 | 100 % | 8.1 / 16.0 | 0.36 / 0.73 | 1779 | 30 |
| run-317 | 23 | 100 % | 6.6 / 13.2 | 0.36 / 0.67 | 1655 | 41 |
| **all (pooled)** | 140 | 100 % | 9.8 / 22.1 | 0.43 / 0.88 | 1720 | 35 |
| **mean of sweep medians** | | | 9.7 | | | |
