# SCR anchors: v1-4XXC on test_4XXE_kabsch_weighted

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine weighted, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-425 | 39 | 100 % | 8.0 / 12.5 | 0.64 / 1.05 | 1583 | 56 |
| run-426 | 39 | 100 % | 4.9 / 17.1 | 0.50 / 0.94 | 1331 | 48 |
| run-427 | 39 | 97 % | 7.8 / 29.3 | 0.82 / 4.07 | 940 | 52 |
| run-428 | 38 | 100 % | 4.0 / 13.7 | 0.45 / 1.52 | 1550 | 54 |
| **all (pooled)** | 155 | 99 % | 6.4 / 16.8 | 0.62 / 1.53 | 1325 | 52 |
| **mean of sweep medians** | | | 6.2 | | | |
