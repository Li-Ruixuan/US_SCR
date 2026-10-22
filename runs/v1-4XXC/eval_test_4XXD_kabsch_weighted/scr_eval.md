# SCR anchors: v1-4XXC on test_4XXD_kabsch_weighted

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine weighted, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-418 | 39 | 100 % | 9.2 / 18.5 | 0.81 / 0.96 | 1452 | 56 |
| run-419 | 39 | 100 % | 9.3 / 12.5 | 0.67 / 0.90 | 1650 | 59 |
| run-420 | 39 | 100 % | 16.9 / 26.2 | 1.05 / 1.57 | 1078 | 55 |
| run-421 | 39 | 100 % | 7.8 / 23.7 | 0.83 / 2.24 | 1075 | 54 |
| run-423 | 39 | 100 % | 11.4 / 22.1 | 0.95 / 1.64 | 1524 | 66 |
| run-424 | 39 | 100 % | 8.3 / 10.6 | 0.74 / 0.90 | 2048 | 67 |
| **all (pooled)** | 234 | 100 % | 10.0 / 21.4 | 0.82 / 1.39 | 1453 | 58 |
| **mean of sweep medians** | | | 10.5 | | | |
