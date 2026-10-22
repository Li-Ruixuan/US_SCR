# SCR anchors: s1-e120-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.4 / 11.1 | 0.30 / 0.58 | 1451 | 53 |
| run-211 | 29 | 100 % | 2.4 / 5.4 | 0.38 / 0.60 | 1269 | 52 |
| **all (pooled)** | 77 | 100 % | 3.4 / 8.7 | 0.33 / 0.58 | 1387 | 52 |
| **mean of sweep medians** | | | 3.4 | | | |
