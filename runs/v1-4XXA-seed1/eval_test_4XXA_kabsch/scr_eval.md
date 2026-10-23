# SCR anchors: v1-4XXA-seed1 on test_4XXA_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 1 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 5.0 / 7.9 | 0.39 / 0.58 | 1944 | 60 |
| run-402 | 37 | 100 % | 5.8 / 8.8 | 0.53 / 0.63 | 1977 | 68 |
| run-403 | 59 | 100 % | 5.3 / 7.4 | 0.52 / 0.74 | 1852 | 58 |
| run-404 | 39 | 100 % | 8.9 / 12.5 | 0.71 / 1.02 | 1654 | 61 |
| run-405 | 38 | 100 % | 6.7 / 10.6 | 0.56 / 0.77 | 1478 | 58 |
| run-406 | 39 | 100 % | 3.6 / 8.4 | 0.39 / 0.46 | 1831 | 52 |
| run-407 | 39 | 100 % | 5.3 / 11.0 | 0.47 / 0.62 | 1830 | 56 |
| run-408 | 39 | 100 % | 6.0 / 12.1 | 0.53 / 0.68 | 1546 | 52 |
| **all (pooled)** | 348 | 100 % | 5.8 / 10.1 | 0.49 / 0.75 | 1802 | 57 |
| **mean of sweep medians** | | | 5.8 | | | |
