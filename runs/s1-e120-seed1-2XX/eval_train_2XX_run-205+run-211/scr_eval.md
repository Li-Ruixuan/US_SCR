# SCR anchors: s1-e120-seed1-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 1 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.9 / 9.5 | 0.23 / 0.40 | 2950 | 8 |
| run-211 | 29 | 100 % | 4.7 / 7.7 | 0.38 / 0.56 | 2281 | 13 |
| **all (pooled)** | 77 | 100 % | 4.9 / 9.4 | 0.29 / 0.51 | 2913 | 8 |
| **mean of sweep medians** | | | 4.8 | | | |
