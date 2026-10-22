# SCR anchors: s1-e120-seed1-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.5 / 10.4 | 0.27 / 0.58 | 1467 | 46 |
| run-211 | 29 | 100 % | 2.5 / 4.8 | 0.43 / 0.60 | 1263 | 46 |
| **all (pooled)** | 77 | 100 % | 3.6 / 9.4 | 0.37 / 0.59 | 1377 | 46 |
| **mean of sweep medians** | | | 3.5 | | | |
