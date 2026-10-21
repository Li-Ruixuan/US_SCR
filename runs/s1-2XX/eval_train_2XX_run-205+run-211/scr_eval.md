# SCR anchors: s1-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 6.5 / 13.7 | 0.30 / 0.53 | 2738 | 9 |
| run-211 | 29 | 100 % | 6.0 / 12.2 | 0.39 / 0.57 | 1960 | 21 |
| **all (pooled)** | 77 | 100 % | 6.3 / 13.1 | 0.34 / 0.55 | 2610 | 10 |
| **mean of sweep medians** | | | 6.3 | | | |
