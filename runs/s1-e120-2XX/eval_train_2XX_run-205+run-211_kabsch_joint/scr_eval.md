# SCR anchors: s1-e120-2XX on train_2XX_run-205+run-211_kabsch_joint

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine joint, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.5 / 10.2 | 0.28 / 0.59 | 1445 | 54 |
| run-211 | 29 | 100 % | 2.8 / 6.3 | 0.40 / 0.58 | 1267 | 51 |
| **all (pooled)** | 77 | 100 % | 3.4 / 9.5 | 0.34 / 0.59 | 1382 | 53 |
| **mean of sweep medians** | | | 3.6 | | | |
