# SCR anchors: v2-3XX on train_3XX_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 1.7 / 2.5 | 0.16 / 0.47 | 2819 | 75 |
| run-314 | 29 | 100 % | 2.2 / 4.1 | 0.18 / 0.28 | 2345 | 70 |
| run-315 | 29 | 100 % | 1.9 / 3.8 | 0.25 / 0.47 | 2616 | 73 |
| run-316 | 30 | 100 % | 1.4 / 2.9 | 0.13 / 0.26 | 2554 | 70 |
| run-317 | 23 | 100 % | 2.0 / 3.7 | 0.27 / 0.42 | 2674 | 73 |
| **all (pooled)** | 140 | 100 % | 1.8 / 3.4 | 0.19 / 0.42 | 2658 | 72 |
| **mean of sweep medians** | | | 1.8 | | | |
