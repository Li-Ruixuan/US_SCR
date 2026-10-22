# SCR anchors: v1-4XXC on test_4XXC_kabsch_weighted

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine weighted, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 4.5 / 5.7 | 0.69 / 0.77 | 1902 | 61 |
| run-414 | 39 | 100 % | 8.4 / 16.0 | 1.08 / 2.19 | 1515 | 58 |
| run-415 | 39 | 100 % | 6.7 / 14.8 | 0.99 / 1.23 | 1544 | 58 |
| run-416 | 39 | 100 % | 6.8 / 13.8 | 0.94 / 1.07 | 1600 | 59 |
| **all (pooled)** | 155 | 100 % | 6.3 / 14.0 | 0.94 / 1.31 | 1605 | 60 |
| **mean of sweep medians** | | | 6.6 | | | |
