# SCR anchors: v2-4XXA on test_4XXB_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 9.6 / 11.5 | 0.39 / 0.50 | 1202 | 63 |
| run-410 | 38 | 100 % | 8.3 / 128.1 | 0.39 / 4.03 | 741 | 49 |
| run-411 | 38 | 100 % | 9.6 / 13.6 | 0.51 / 0.76 | 833 | 53 |
| run-412 | 39 | 100 % | 9.9 / 14.7 | 0.61 / 0.80 | 766 | 49 |
| **all (pooled)** | 155 | 100 % | 9.6 / 13.8 | 0.46 / 0.76 | 828 | 52 |
| **mean of sweep medians** | | | 9.4 | | | |
