# SCR anchors: bigclean-2XX on train_2XX_run-205+run-211

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.8 / 11.2 | 0.23 / 0.43 | 2230 | 14 |
| run-211 | 29 | 100 % | 5.2 / 8.1 | 0.37 / 0.54 | 1869 | 25 |
| **all (pooled)** | 77 | 100 % | 4.8 / 10.9 | 0.27 / 0.51 | 2190 | 15 |
| **mean of sweep medians** | | | 5.0 | | | |
