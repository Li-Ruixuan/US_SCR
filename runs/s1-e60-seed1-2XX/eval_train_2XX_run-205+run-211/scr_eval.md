# SCR anchors: s1-e60-seed1-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 1 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 6.2 / 12.7 | 0.24 / 0.55 | 2846 | 9 |
| run-211 | 29 | 100 % | 6.5 / 13.0 | 0.41 / 0.61 | 2146 | 15 |
| **all (pooled)** | 77 | 100 % | 6.3 / 12.9 | 0.31 / 0.61 | 2766 | 9 |
| **mean of sweep medians** | | | 6.3 | | | |
