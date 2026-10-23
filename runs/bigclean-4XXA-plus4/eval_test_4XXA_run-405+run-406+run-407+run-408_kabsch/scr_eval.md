# SCR anchors: bigclean-4XXA-plus4 on test_4XXA_run-405+run-406+run-407+run-408_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 1.8 / 5.9 | 0.19 / 0.42 | 1950 | 59 |
| run-406 | 39 | 100 % | 1.0 / 2.7 | 0.30 / 0.40 | 2005 | 50 |
| run-407 | 39 | 100 % | 2.3 / 3.8 | 0.13 / 0.29 | 2074 | 55 |
| run-408 | 39 | 100 % | 2.3 / 5.0 | 0.22 / 0.42 | 1815 | 49 |
| **all (pooled)** | 155 | 100 % | 2.0 / 5.2 | 0.22 / 0.40 | 1986 | 52 |
| **mean of sweep medians** | | | 1.8 | | | |
