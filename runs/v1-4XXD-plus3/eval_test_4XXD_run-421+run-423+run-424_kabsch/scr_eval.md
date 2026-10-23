# SCR anchors: v1-4XXD-plus3 on test_4XXD_run-421+run-423+run-424_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-421 | 39 | 100 % | 1.8 / 9.1 | 0.16 / 0.37 | 1791 | 53 |
| run-423 | 39 | 100 % | 4.4 / 8.0 | 0.44 / 0.62 | 2050 | 66 |
| run-424 | 39 | 100 % | 3.1 / 4.7 | 0.18 / 0.30 | 2470 | 67 |
| **all (pooled)** | 117 | 100 % | 3.3 / 7.0 | 0.22 / 0.54 | 2091 | 64 |
| **mean of sweep medians** | | | 3.1 | | | |
