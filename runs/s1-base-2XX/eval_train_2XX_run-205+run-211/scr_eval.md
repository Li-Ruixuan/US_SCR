# SCR anchors: s1-base-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 14.0 / 29.2 | 0.54 / 1.05 | 1632 | 52 |
| run-211 | 29 | 100 % | 17.7 / 30.8 | 0.59 / 1.20 | 888 | 221 |
| **all (pooled)** | 77 | 100 % | 15.8 / 31.3 | 0.55 / 1.10 | 1443 | 81 |
| **mean of sweep medians** | | | 15.8 | | | |
