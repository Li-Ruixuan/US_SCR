# SCR anchors: v1-4XXA-plus4 on test_4XXA_run-405+run-406+run-407+run-408_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 1.7 / 5.7 | 0.21 / 0.39 | 1941 | 59 |
| run-406 | 39 | 100 % | 1.1 / 2.7 | 0.30 / 0.44 | 2008 | 50 |
| run-407 | 39 | 100 % | 2.2 / 3.9 | 0.15 / 0.34 | 2081 | 55 |
| run-408 | 39 | 100 % | 2.4 / 5.7 | 0.19 / 0.41 | 1804 | 50 |
| **all (pooled)** | 155 | 100 % | 2.0 / 5.5 | 0.22 / 0.41 | 1970 | 52 |
| **mean of sweep medians** | | | 1.9 | | | |
