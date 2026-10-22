# SCR anchors: aug-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 6.3 / 10.7 | 0.35 / 0.55 | 1382 | 53 |
| run-211 | 29 | 100 % | 6.7 / 9.5 | 0.42 / 0.64 | 1252 | 45 |
| **all (pooled)** | 77 | 100 % | 6.3 / 10.1 | 0.37 / 0.60 | 1323 | 48 |
| **mean of sweep medians** | | | 6.5 | | | |
