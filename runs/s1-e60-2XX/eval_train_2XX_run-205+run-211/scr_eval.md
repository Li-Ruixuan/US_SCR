# SCR anchors: s1-e60-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.9 / 11.1 | 0.25 / 0.45 | 2850 | 10 |
| run-211 | 29 | 100 % | 6.0 / 12.0 | 0.31 / 0.47 | 2139 | 20 |
| **all (pooled)** | 77 | 100 % | 5.3 / 11.3 | 0.26 / 0.47 | 2793 | 10 |
| **mean of sweep medians** | | | 5.4 | | | |
