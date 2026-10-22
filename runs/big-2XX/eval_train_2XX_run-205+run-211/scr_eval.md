# SCR anchors: big-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.4 / 10.1 | 0.22 / 0.50 | 3020 | 8 |
| run-211 | 29 | 100 % | 4.8 / 9.1 | 0.40 / 0.47 | 2211 | 14 |
| **all (pooled)** | 77 | 100 % | 4.7 / 9.6 | 0.27 / 0.48 | 2959 | 9 |
| **mean of sweep medians** | | | 4.6 | | | |
