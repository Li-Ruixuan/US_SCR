# SCR anchors: v1-3XX on train_3XX_kabsch_joint

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine joint, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 2.4 / 2.8 | 0.18 / 0.48 | 2809 | 85 |
| run-314 | 29 | 100 % | 2.1 / 3.9 | 0.19 / 0.24 | 2307 | 78 |
| run-315 | 29 | 100 % | 2.1 / 4.1 | 0.19 / 0.43 | 2628 | 82 |
| run-316 | 30 | 100 % | 1.3 / 2.9 | 0.13 / 0.22 | 2530 | 79 |
| run-317 | 23 | 100 % | 2.0 / 4.0 | 0.25 / 0.37 | 2665 | 82 |
| **all (pooled)** | 140 | 100 % | 2.0 / 3.9 | 0.18 / 0.39 | 2643 | 81 |
| **mean of sweep medians** | | | 2.0 | | | |
