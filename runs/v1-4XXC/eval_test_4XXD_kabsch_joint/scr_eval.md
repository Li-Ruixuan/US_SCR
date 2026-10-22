# SCR anchors: v1-4XXC on test_4XXD_kabsch_joint

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine joint, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-418 | 39 | 100 % | 9.6 / 20.1 | 0.77 / 0.91 | 1469 | 64 |
| run-419 | 39 | 100 % | 10.3 / 15.8 | 0.72 / 0.89 | 1665 | 68 |
| run-420 | 39 | 100 % | 16.6 / 29.0 | 1.02 / 1.44 | 1077 | 62 |
| run-421 | 39 | 100 % | 10.6 / 24.1 | 0.79 / 1.59 | 1109 | 60 |
| run-423 | 39 | 100 % | 13.2 / 22.2 | 0.93 / 1.62 | 1582 | 76 |
| run-424 | 39 | 100 % | 10.7 / 12.6 | 0.81 / 0.94 | 2080 | 78 |
| **all (pooled)** | 234 | 100 % | 11.5 / 21.7 | 0.84 / 1.36 | 1493 | 66 |
| **mean of sweep medians** | | | 11.8 | | | |
