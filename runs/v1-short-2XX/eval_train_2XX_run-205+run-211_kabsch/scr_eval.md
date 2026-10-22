# SCR anchors: v1-short-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 9.8 / 34.8 | 0.52 / 1.33 | 628 | 49 |
| run-211 | 29 | 100 % | 22.6 / 34.5 | 1.59 / 3.38 | 235 | 44 |
| **all (pooled)** | 77 | 100 % | 14.7 / 34.7 | 0.96 / 2.33 | 527 | 47 |
| **mean of sweep medians** | | | 16.2 | | | |
