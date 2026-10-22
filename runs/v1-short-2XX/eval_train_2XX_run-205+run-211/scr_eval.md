# SCR anchors: v1-short-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 35.3 / 72.7 | 1.00 / 1.59 | 1270 | 143 |
| run-211 | 29 | 100 % | 45.0 / 81.1 | 2.14 / 3.58 | 307 | 221 |
| **all (pooled)** | 77 | 100 % | 40.5 / 77.5 | 1.20 / 2.53 | 1067 | 221 |
| **mean of sweep medians** | | | 40.2 | | | |
