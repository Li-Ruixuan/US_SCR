# SCR anchors: v1-3XX on train_3XX_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 1.9 / 2.4 | 0.19 / 0.41 | 2808 | 74 |
| run-314 | 29 | 100 % | 2.3 / 4.1 | 0.20 / 0.30 | 2296 | 69 |
| run-315 | 29 | 100 % | 2.1 / 4.2 | 0.24 / 0.46 | 2621 | 73 |
| run-316 | 30 | 100 % | 1.3 / 3.0 | 0.12 / 0.28 | 2528 | 71 |
| run-317 | 23 | 100 % | 2.1 / 3.0 | 0.24 / 0.40 | 2662 | 73 |
| **all (pooled)** | 140 | 100 % | 1.9 / 3.3 | 0.19 / 0.38 | 2646 | 72 |
| **mean of sweep medians** | | | 2.0 | | | |
