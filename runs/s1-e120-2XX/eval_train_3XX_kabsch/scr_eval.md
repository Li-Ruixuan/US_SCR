# SCR anchors: s1-e120-2XX on train_3XX_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-313 | 29 | 100 % | 7.2 / 10.0 | 0.41 / 0.60 | 1446 | 74 |
| run-314 | 29 | 100 % | 4.3 / 6.5 | 0.37 / 0.57 | 1411 | 69 |
| run-315 | 29 | 100 % | 6.7 / 13.8 | 0.43 / 0.66 | 1413 | 73 |
| run-316 | 30 | 100 % | 5.8 / 9.9 | 0.52 / 0.87 | 1254 | 71 |
| run-317 | 23 | 100 % | 8.3 / 22.0 | 0.55 / 0.74 | 1119 | 72 |
| **all (pooled)** | 140 | 100 % | 6.0 / 11.8 | 0.44 / 0.67 | 1344 | 72 |
| **mean of sweep medians** | | | 6.5 | | | |
