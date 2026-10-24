# SCR anchors: v1-3XX-room301 on train_3XX_run-315+run-316+run-317_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-315 | 29 | 100 % | 4.0 / 6.5 | 0.31 / 0.58 | 2502 | 73 |
| run-316 | 30 | 100 % | 2.3 / 5.1 | 0.21 / 0.37 | 2489 | 70 |
| run-317 | 23 | 100 % | 3.1 / 5.8 | 0.31 / 0.49 | 2503 | 72 |
| **all (pooled)** | 82 | 100 % | 3.3 / 6.1 | 0.26 / 0.51 | 2500 | 72 |
| **mean of sweep medians** | | | 3.1 | | | |
