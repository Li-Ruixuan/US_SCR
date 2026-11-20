# SCR anchors: bigclean-2XX on train_3XX_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 3.0 / 4.7 | 0.43 / 0.51 | 1726 | 76 |
| run-314 | 29 | 100 % | 3.8 / 6.3 | 0.41 / 0.54 | 1548 | 70 |
| run-315 | 29 | 100 % | 3.6 / 9.2 | 0.33 / 0.60 | 1569 | 72 |
| run-316 | 30 | 100 % | 6.8 / 8.8 | 0.53 / 0.78 | 1333 | 70 |
| run-317 | 23 | 100 % | 6.5 / 10.6 | 0.44 / 0.62 | 1252 | 73 |
| **all (pooled)** | 140 | 100 % | 4.4 / 9.3 | 0.44 / 0.64 | 1478 | 72 |
| **mean of sweep medians** | | | 4.7 | | | |
