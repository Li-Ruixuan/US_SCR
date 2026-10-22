# SCR anchors: clean-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.3 / 8.6 | 0.24 / 0.50 | 1483 | 46 |
| run-211 | 29 | 100 % | 2.7 / 4.6 | 0.44 / 0.62 | 1268 | 44 |
| **all (pooled)** | 77 | 100 % | 3.5 / 8.0 | 0.31 / 0.61 | 1392 | 45 |
| **mean of sweep medians** | | | 3.5 | | | |
