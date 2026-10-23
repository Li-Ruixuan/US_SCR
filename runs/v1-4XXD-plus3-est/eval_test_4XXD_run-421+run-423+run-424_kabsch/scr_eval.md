# SCR anchors: v1-4XXD-plus3-est on test_4XXD_run-421+run-423+run-424_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-421 | 39 | 100 % | 8.6 / 19.9 | 0.63 / 1.18 | 1777 | 53 |
| run-423 | 39 | 100 % | 7.8 / 10.5 | 0.57 / 0.88 | 2041 | 66 |
| run-424 | 39 | 100 % | 7.1 / 8.4 | 0.61 / 0.68 | 2469 | 67 |
| **all (pooled)** | 117 | 100 % | 7.5 / 11.2 | 0.60 / 0.90 | 2082 | 64 |
| **mean of sweep medians** | | | 7.9 | | | |
