# SCR anchors: v2-4XXA on test_4XXC_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 11.2 / 97.1 | 0.63 / 3.18 | 454 | 61 |
| run-414 | 39 | 100 % | 11.1 / 110.2 | 2.03 / 3.78 | 413 | 59 |
| run-415 | 39 | 100 % | 9.4 / 17.7 | 0.51 / 0.96 | 403 | 60 |
| run-416 | 39 | 100 % | 15.7 / 99.1 | 0.64 / 3.35 | 392 | 61 |
| **all (pooled)** | 155 | 100 % | 11.0 / 98.4 | 0.64 / 3.37 | 430 | 60 |
| **mean of sweep medians** | | | 11.8 | | | |
