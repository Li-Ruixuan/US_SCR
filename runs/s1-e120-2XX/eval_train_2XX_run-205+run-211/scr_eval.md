# SCR anchors: s1-e120-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 5.3 / 10.7 | 0.26 / 0.47 | 2966 | 8 |
| run-211 | 29 | 100 % | 4.9 / 11.2 | 0.40 / 0.55 | 2205 | 14 |
| **all (pooled)** | 77 | 100 % | 5.1 / 11.3 | 0.31 / 0.53 | 2901 | 9 |
| **mean of sweep medians** | | | 5.1 | | | |
