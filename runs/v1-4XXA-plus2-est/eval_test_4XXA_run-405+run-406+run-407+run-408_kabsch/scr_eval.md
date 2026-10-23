# SCR anchors: v1-4XXA-plus2-est on test_4XXA_run-405+run-406+run-407+run-408_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 7.2 / 9.1 | 0.52 / 0.79 | 1852 | 63 |
| run-406 | 39 | 100 % | 3.5 / 7.6 | 0.36 / 0.45 | 1977 | 50 |
| run-407 | 39 | 100 % | 4.6 / 8.7 | 0.49 / 0.60 | 2040 | 56 |
| run-408 | 39 | 100 % | 4.8 / 9.4 | 0.53 / 0.67 | 1766 | 50 |
| **all (pooled)** | 155 | 100 % | 5.3 / 8.4 | 0.48 / 0.67 | 1939 | 53 |
| **mean of sweep medians** | | | 5.0 | | | |
