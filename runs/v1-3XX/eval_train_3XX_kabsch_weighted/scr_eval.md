# SCR anchors: v1-3XX on train_3XX_kabsch_weighted

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine weighted, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 2.2 / 3.1 | 0.19 / 0.47 | 2813 | 74 |
| run-314 | 29 | 100 % | 1.9 / 5.9 | 0.24 / 0.35 | 2293 | 68 |
| run-315 | 29 | 100 % | 2.7 / 6.0 | 0.19 / 0.64 | 2609 | 72 |
| run-316 | 30 | 100 % | 1.4 / 3.5 | 0.16 / 0.34 | 2528 | 69 |
| run-317 | 23 | 100 % | 2.2 / 3.7 | 0.23 / 0.50 | 2668 | 72 |
| **all (pooled)** | 140 | 100 % | 2.2 / 4.6 | 0.21 / 0.47 | 2638 | 71 |
| **mean of sweep medians** | | | 2.1 | | | |
