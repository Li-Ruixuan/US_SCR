# SCR anchors: v1-4XXA on test_4XXA_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 5.3 / 8.2 | 0.38 / 0.54 | 1952 | 59 |
| run-402 | 37 | 100 % | 6.1 / 8.2 | 0.51 / 0.59 | 1955 | 66 |
| run-403 | 59 | 100 % | 5.6 / 7.6 | 0.46 / 0.64 | 1803 | 57 |
| run-404 | 39 | 100 % | 8.9 / 14.3 | 0.61 / 1.06 | 1593 | 61 |
| run-405 | 38 | 100 % | 7.1 / 11.9 | 0.50 / 0.85 | 1444 | 58 |
| run-406 | 39 | 100 % | 2.9 / 8.1 | 0.38 / 0.47 | 1793 | 51 |
| run-407 | 39 | 100 % | 5.0 / 11.5 | 0.46 / 0.70 | 1847 | 55 |
| run-408 | 39 | 100 % | 6.0 / 11.1 | 0.54 / 0.83 | 1534 | 48 |
| **all (pooled)** | 348 | 100 % | 6.3 / 10.1 | 0.48 / 0.74 | 1792 | 56 |
| **mean of sweep medians** | | | 5.9 | | | |
