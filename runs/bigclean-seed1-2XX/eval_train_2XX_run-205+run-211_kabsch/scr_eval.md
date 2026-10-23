# SCR anchors: bigclean-seed1-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 1 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 3.4 / 7.8 | 0.27 / 0.46 | 1485 | 47 |
| run-211 | 29 | 100 % | 4.0 / 6.6 | 0.31 / 0.52 | 1310 | 46 |
| **all (pooled)** | 77 | 100 % | 3.5 / 6.9 | 0.28 / 0.49 | 1432 | 47 |
| **mean of sweep medians** | | | 3.7 | | | |
