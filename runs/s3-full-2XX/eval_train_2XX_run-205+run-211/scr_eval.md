# SCR anchors: s3-full-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 6.6 / 13.8 | 0.32 / 0.55 | 10054 | 27 |
| run-211 | 29 | 100 % | 7.9 / 15.1 | 0.34 / 0.53 | 6859 | 101 |
| **all (pooled)** | 77 | 100 % | 7.1 / 14.5 | 0.33 / 0.55 | 9573 | 30 |
| **mean of sweep medians** | | | 7.3 | | | |
