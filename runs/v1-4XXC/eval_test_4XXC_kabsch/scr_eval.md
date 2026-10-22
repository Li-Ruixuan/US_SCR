# SCR anchors: v1-4XXC on test_4XXC_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 3.5 / 5.2 | 0.67 / 0.77 | 1934 | 61 |
| run-414 | 39 | 100 % | 5.8 / 11.2 | 0.90 / 1.08 | 1626 | 59 |
| run-415 | 39 | 100 % | 5.6 / 9.2 | 0.75 / 1.00 | 1583 | 58 |
| run-416 | 39 | 100 % | 5.9 / 10.8 | 0.69 / 0.91 | 1624 | 60 |
| **all (pooled)** | 155 | 100 % | 5.2 / 10.1 | 0.74 / 0.99 | 1643 | 59 |
| **mean of sweep medians** | | | 5.2 | | | |
