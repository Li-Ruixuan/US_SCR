# SCR anchors: v1-4XXA-plus1 on test_4XXA_run-405+run-406+run-407+run-408_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 4.7 / 11.6 | 0.36 / 0.54 | 1704 | 59 |
| run-406 | 39 | 100 % | 1.2 / 2.6 | 0.27 / 0.41 | 1973 | 50 |
| run-407 | 39 | 100 % | 2.0 / 4.7 | 0.21 / 0.36 | 2023 | 55 |
| run-408 | 39 | 100 % | 1.8 / 4.4 | 0.23 / 0.46 | 1784 | 50 |
| **all (pooled)** | 155 | 100 % | 2.0 / 6.6 | 0.27 / 0.47 | 1928 | 52 |
| **mean of sweep medians** | | | 2.4 | | | |
