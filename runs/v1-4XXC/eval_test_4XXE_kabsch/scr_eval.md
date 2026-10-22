# SCR anchors: v1-4XXC on test_4XXE_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-425 | 39 | 100 % | 6.2 / 10.2 | 0.43 / 0.71 | 1615 | 57 |
| run-426 | 39 | 100 % | 4.5 / 13.0 | 0.38 / 0.64 | 1359 | 49 |
| run-427 | 39 | 97 % | 8.8 / 28.8 | 0.73 / 3.71 | 1041 | 52 |
| run-428 | 38 | 100 % | 4.0 / 11.9 | 0.39 / 0.64 | 1574 | 54 |
| **all (pooled)** | 155 | 99 % | 6.5 / 13.9 | 0.46 / 0.84 | 1348 | 52 |
| **mean of sweep medians** | | | 5.9 | | | |
