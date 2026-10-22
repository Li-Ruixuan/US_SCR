# SCR anchors: clean-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 6.0 / 10.9 | 0.20 / 0.54 | 2221 | 14 |
| run-211 | 29 | 100 % | 6.1 / 8.8 | 0.46 / 0.55 | 1835 | 27 |
| **all (pooled)** | 77 | 100 % | 6.1 / 10.3 | 0.31 / 0.55 | 2175 | 15 |
| **mean of sweep medians** | | | 6.1 | | | |
