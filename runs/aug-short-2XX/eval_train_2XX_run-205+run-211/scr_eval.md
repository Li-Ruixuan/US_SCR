# SCR anchors: aug-short-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 24.7 / 58.5 | 0.73 / 1.79 | 1347 | 116 |
| run-211 | 29 | 100 % | 21.6 / 33.9 | 0.74 / 1.21 | 984 | 221 |
| **all (pooled)** | 77 | 100 % | 23.8 / 53.9 | 0.74 / 1.51 | 1275 | 139 |
| **mean of sweep medians** | | | 23.2 | | | |
