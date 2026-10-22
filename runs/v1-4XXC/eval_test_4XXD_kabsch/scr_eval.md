# SCR anchors: v1-4XXC on test_4XXD_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-418 | 39 | 100 % | 7.5 / 17.0 | 0.69 / 0.82 | 1477 | 56 |
| run-419 | 39 | 100 % | 7.6 / 13.5 | 0.62 / 0.76 | 1684 | 60 |
| run-420 | 39 | 100 % | 13.8 / 26.6 | 0.93 / 1.27 | 1093 | 54 |
| run-421 | 39 | 100 % | 9.1 / 24.3 | 0.76 / 1.67 | 1152 | 54 |
| run-423 | 39 | 100 % | 10.1 / 18.2 | 0.82 / 1.36 | 1592 | 66 |
| run-424 | 39 | 100 % | 7.6 / 9.2 | 0.68 / 0.77 | 2093 | 67 |
| **all (pooled)** | 234 | 100 % | 8.7 / 18.9 | 0.73 / 1.19 | 1497 | 59 |
| **mean of sweep medians** | | | 9.3 | | | |
