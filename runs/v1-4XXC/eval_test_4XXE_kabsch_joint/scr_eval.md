# SCR anchors: v1-4XXC on test_4XXE_kabsch_joint

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine joint, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-425 | 39 | 100 % | 8.2 / 12.0 | 0.50 / 0.80 | 1616 | 65 |
| run-426 | 39 | 100 % | 5.6 / 14.3 | 0.52 / 0.64 | 1351 | 56 |
| run-427 | 39 | 97 % | 11.2 / 28.5 | 0.80 / 3.60 | 995 | 58 |
| run-428 | 38 | 100 % | 4.2 / 15.0 | 0.40 / 0.91 | 1562 | 61 |
| **all (pooled)** | 155 | 99 % | 7.8 / 15.5 | 0.58 / 0.97 | 1346 | 59 |
| **mean of sweep medians** | | | 7.3 | | | |
