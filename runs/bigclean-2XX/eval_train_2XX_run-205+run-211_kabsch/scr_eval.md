# SCR anchors: bigclean-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.0 / 8.3 | 0.23 / 0.43 | 1485 | 46 |
| run-211 | 29 | 100 % | 2.7 / 4.6 | 0.33 / 0.51 | 1262 | 45 |
| **all (pooled)** | 77 | 100 % | 3.2 / 7.3 | 0.27 / 0.50 | 1398 | 45 |
| **mean of sweep medians** | | | 3.4 | | | |
