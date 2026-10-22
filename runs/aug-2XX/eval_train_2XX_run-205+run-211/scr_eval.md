# SCR anchors: aug-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 7.0 / 15.8 | 0.32 / 0.47 | 2827 | 9 |
| run-211 | 29 | 100 % | 6.1 / 11.3 | 0.39 / 0.55 | 2375 | 11 |
| **all (pooled)** | 77 | 100 % | 6.9 / 13.5 | 0.33 / 0.53 | 2762 | 9 |
| **mean of sweep medians** | | | 6.6 | | | |
