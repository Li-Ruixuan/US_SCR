# SCR anchors: v1-3XX-seed1 on train_3XX_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 1 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 1.8 / 2.2 | 0.14 / 0.42 | 2809 | 74 |
| run-314 | 29 | 100 % | 2.5 / 4.9 | 0.18 / 0.31 | 2312 | 69 |
| run-315 | 29 | 100 % | 2.1 / 4.5 | 0.24 / 0.49 | 2613 | 73 |
| run-316 | 30 | 100 % | 1.1 / 3.1 | 0.15 / 0.26 | 2535 | 70 |
| run-317 | 23 | 100 % | 2.1 / 3.4 | 0.25 / 0.37 | 2677 | 73 |
| **all (pooled)** | 140 | 100 % | 1.8 / 3.6 | 0.18 / 0.37 | 2648 | 72 |
| **mean of sweep medians** | | | 1.9 | | | |
