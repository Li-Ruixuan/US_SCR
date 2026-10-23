# SCR anchors: v1-3XX-seed2 on train_3XX_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 2 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 2.5 / 3.2 | 0.18 / 0.43 | 2824 | 75 |
| run-314 | 29 | 100 % | 2.7 / 4.9 | 0.20 / 0.35 | 2308 | 70 |
| run-315 | 29 | 100 % | 2.2 / 4.6 | 0.22 / 0.48 | 2628 | 73 |
| run-316 | 30 | 100 % | 1.3 / 3.5 | 0.15 / 0.29 | 2530 | 70 |
| run-317 | 23 | 100 % | 2.1 / 3.6 | 0.29 / 0.40 | 2658 | 73 |
| **all (pooled)** | 140 | 100 % | 2.2 / 3.8 | 0.19 / 0.41 | 2634 | 72 |
| **mean of sweep medians** | | | 2.2 | | | |
