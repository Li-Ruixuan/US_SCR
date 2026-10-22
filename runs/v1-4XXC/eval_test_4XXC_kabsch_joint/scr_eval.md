# SCR anchors: v1-4XXC on test_4XXC_kabsch_joint

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine joint, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 3.4 / 5.1 | 0.59 / 0.68 | 1926 | 70 |
| run-414 | 39 | 100 % | 6.0 / 14.3 | 0.90 / 1.30 | 1590 | 66 |
| run-415 | 39 | 100 % | 6.7 / 14.2 | 0.83 / 1.06 | 1561 | 65 |
| run-416 | 39 | 100 % | 6.6 / 13.4 | 0.82 / 1.01 | 1613 | 66 |
| **all (pooled)** | 155 | 100 % | 5.5 / 13.2 | 0.80 / 1.08 | 1629 | 67 |
| **mean of sweep medians** | | | 5.7 | | | |
