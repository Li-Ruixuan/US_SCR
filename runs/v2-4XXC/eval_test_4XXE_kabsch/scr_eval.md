# SCR anchors: v2-4XXC on test_4XXE_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-425 | 39 | 100 % | 6.4 / 9.4 | 0.39 / 0.56 | 1643 | 57 |
| run-426 | 39 | 100 % | 6.8 / 10.2 | 0.36 / 0.66 | 1379 | 49 |
| run-427 | 39 | 92 % | 7.0 / 17.8 | 0.57 / 2.11 | 1129 | 52 |
| run-428 | 38 | 100 % | 2.4 / 7.6 | 0.30 / 0.54 | 1638 | 55 |
| **all (pooled)** | 155 | 98 % | 6.2 / 9.7 | 0.40 / 0.68 | 1381 | 52 |
| **mean of sweep medians** | | | 5.7 | | | |
