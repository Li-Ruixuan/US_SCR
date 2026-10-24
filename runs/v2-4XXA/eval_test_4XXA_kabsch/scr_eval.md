# SCR anchors: v2-4XXA on test_4XXA_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 4.1 / 6.4 | 0.36 / 0.56 | 1961 | 60 |
| run-402 | 37 | 100 % | 6.5 / 7.6 | 0.49 / 0.64 | 2012 | 68 |
| run-403 | 59 | 100 % | 5.9 / 7.5 | 0.47 / 0.60 | 1870 | 58 |
| run-404 | 39 | 100 % | 9.0 / 12.9 | 0.65 / 1.18 | 1622 | 62 |
| run-405 | 38 | 100 % | 6.2 / 9.1 | 0.57 / 0.80 | 1524 | 59 |
| run-406 | 39 | 100 % | 3.5 / 6.6 | 0.38 / 0.48 | 1822 | 52 |
| run-407 | 39 | 100 % | 3.7 / 6.6 | 0.39 / 0.67 | 1871 | 56 |
| run-408 | 39 | 100 % | 4.7 / 8.0 | 0.47 / 0.78 | 1627 | 52 |
| **all (pooled)** | 348 | 100 % | 5.3 / 8.9 | 0.45 / 0.71 | 1820 | 57 |
| **mean of sweep medians** | | | 5.4 | | | |
