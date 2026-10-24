# SCR anchors: v2-4XXC on test_4XXC_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 3.8 / 4.6 | 0.54 / 0.59 | 2021 | 63 |
| run-414 | 39 | 100 % | 6.6 / 14.5 | 0.74 / 1.02 | 1725 | 59 |
| run-415 | 39 | 100 % | 4.0 / 7.7 | 0.60 / 0.85 | 1652 | 58 |
| run-416 | 39 | 100 % | 4.7 / 10.2 | 0.59 / 0.82 | 1696 | 61 |
| **all (pooled)** | 155 | 100 % | 4.5 / 9.9 | 0.59 / 0.86 | 1756 | 61 |
| **mean of sweep medians** | | | 4.8 | | | |
