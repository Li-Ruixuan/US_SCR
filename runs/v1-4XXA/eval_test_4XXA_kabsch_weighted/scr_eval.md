# SCR anchors: v1-4XXA on test_4XXA_kabsch_weighted

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine weighted, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 7.0 / 11.7 | 0.49 / 0.72 | 1917 | 59 |
| run-402 | 37 | 100 % | 7.5 / 13.2 | 0.75 / 0.95 | 1884 | 66 |
| run-403 | 59 | 100 % | 6.4 / 9.2 | 0.41 / 0.83 | 1737 | 56 |
| run-404 | 39 | 100 % | 9.5 / 14.8 | 0.69 / 0.94 | 1521 | 60 |
| run-405 | 38 | 100 % | 10.0 / 12.8 | 0.63 / 0.78 | 1415 | 58 |
| run-406 | 39 | 100 % | 5.4 / 8.5 | 0.36 / 0.64 | 1718 | 50 |
| run-407 | 39 | 100 % | 4.7 / 11.2 | 0.56 / 0.86 | 1780 | 55 |
| run-408 | 39 | 100 % | 6.9 / 13.0 | 0.72 / 0.95 | 1423 | 48 |
| **all (pooled)** | 348 | 100 % | 6.9 / 12.0 | 0.54 / 0.87 | 1695 | 56 |
| **mean of sweep medians** | | | 7.2 | | | |
