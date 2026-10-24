# SCR anchors: v2-4XXC on test_4XXD_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-418 | 39 | 100 % | 6.7 / 13.6 | 0.57 / 0.71 | 1518 | 57 |
| run-419 | 39 | 100 % | 6.7 / 13.0 | 0.49 / 0.67 | 1731 | 60 |
| run-420 | 39 | 100 % | 12.0 / 18.0 | 0.72 / 0.93 | 1142 | 55 |
| run-421 | 39 | 100 % | 7.6 / 15.0 | 0.66 / 1.51 | 1192 | 54 |
| run-423 | 39 | 100 % | 10.6 / 13.7 | 0.85 / 1.07 | 1635 | 67 |
| run-424 | 39 | 100 % | 7.9 / 9.1 | 0.62 / 0.70 | 2116 | 68 |
| **all (pooled)** | 234 | 100 % | 8.2 / 14.5 | 0.64 / 0.92 | 1530 | 59 |
| **mean of sweep medians** | | | 8.6 | | | |
