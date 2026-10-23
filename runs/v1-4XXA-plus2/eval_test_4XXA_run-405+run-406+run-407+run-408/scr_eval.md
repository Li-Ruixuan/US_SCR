# SCR anchors: v1-4XXA-plus2 on test_4XXA_run-405+run-406+run-407+run-408

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 3.6 / 12.4 | 0.25 / 0.48 | 2892 | 9 |
| run-406 | 39 | 100 % | 1.8 / 3.5 | 0.34 / 0.47 | 3028 | 8 |
| run-407 | 39 | 100 % | 2.0 / 4.3 | 0.18 / 0.38 | 3120 | 8 |
| run-408 | 39 | 100 % | 3.2 / 9.7 | 0.21 / 0.42 | 2859 | 9 |
| **all (pooled)** | 155 | 100 % | 2.6 / 8.5 | 0.26 / 0.44 | 2956 | 8 |
| **mean of sweep medians** | | | 2.7 | | | |
