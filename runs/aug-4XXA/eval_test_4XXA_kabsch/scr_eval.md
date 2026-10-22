# SCR anchors: aug-4XXA on test_4XXA_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 3.7 / 7.1 | 0.37 / 0.50 | 1900 | 59 |
| run-402 | 37 | 100 % | 4.6 / 8.1 | 0.46 / 0.62 | 2034 | 67 |
| run-403 | 59 | 100 % | 4.9 / 6.1 | 0.58 / 0.73 | 1850 | 57 |
| run-404 | 39 | 100 % | 5.2 / 7.1 | 0.70 / 0.86 | 1686 | 61 |
| run-405 | 38 | 100 % | 4.2 / 7.0 | 0.45 / 0.67 | 1516 | 59 |
| run-406 | 39 | 100 % | 5.2 / 6.2 | 0.27 / 0.47 | 1781 | 51 |
| run-407 | 39 | 100 % | 7.7 / 10.6 | 0.39 / 0.51 | 1824 | 56 |
| run-408 | 39 | 100 % | 5.0 / 8.5 | 0.39 / 0.56 | 1578 | 54 |
| **all (pooled)** | 348 | 100 % | 4.9 / 8.1 | 0.42 / 0.70 | 1804 | 57 |
| **mean of sweep medians** | | | 5.1 | | | |
