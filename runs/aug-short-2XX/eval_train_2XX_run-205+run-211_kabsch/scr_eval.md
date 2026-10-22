# SCR anchors: aug-short-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 11.8 / 29.1 | 0.54 / 1.15 | 711 | 46 |
| run-211 | 29 | 100 % | 24.7 / 39.4 | 0.98 / 2.52 | 451 | 44 |
| **all (pooled)** | 77 | 100 % | 17.0 / 36.4 | 0.67 / 1.51 | 666 | 45 |
| **mean of sweep medians** | | | 18.2 | | | |
