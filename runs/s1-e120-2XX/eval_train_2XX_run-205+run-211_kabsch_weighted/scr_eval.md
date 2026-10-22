# SCR anchors: s1-e120-2XX on train_2XX_run-205+run-211_kabsch_weighted

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine weighted, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.7 / 10.7 | 0.31 / 0.57 | 1444 | 50 |
| run-211 | 29 | 100 % | 4.8 / 7.5 | 0.48 / 0.64 | 1258 | 46 |
| **all (pooled)** | 77 | 100 % | 4.8 / 9.5 | 0.37 / 0.63 | 1377 | 47 |
| **mean of sweep medians** | | | 4.7 | | | |
