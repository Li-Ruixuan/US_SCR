# SCR anchors: v1-4XXA-plus2 on test_4XXA_run-405+run-406+run-407+run-408_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 2.5 / 10.2 | 0.24 / 0.46 | 1836 | 59 |
| run-406 | 39 | 100 % | 1.1 / 3.0 | 0.30 / 0.44 | 1999 | 50 |
| run-407 | 39 | 100 % | 1.9 / 4.4 | 0.12 / 0.34 | 2047 | 55 |
| run-408 | 39 | 100 % | 2.2 / 5.3 | 0.18 / 0.44 | 1803 | 50 |
| **all (pooled)** | 155 | 100 % | 1.9 / 5.4 | 0.23 / 0.43 | 1963 | 52 |
| **mean of sweep medians** | | | 1.9 | | | |
