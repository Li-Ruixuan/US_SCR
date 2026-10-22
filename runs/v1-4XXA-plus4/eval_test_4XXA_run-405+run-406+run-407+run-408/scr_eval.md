# SCR anchors: v1-4XXA-plus4 on test_4XXA_run-405+run-406+run-407+run-408

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 2.6 / 7.3 | 0.19 / 0.37 | 3140 | 8 |
| run-406 | 39 | 100 % | 2.0 / 3.2 | 0.33 / 0.43 | 3129 | 8 |
| run-407 | 39 | 100 % | 2.0 / 3.9 | 0.23 / 0.39 | 3213 | 8 |
| run-408 | 39 | 100 % | 3.0 / 13.3 | 0.24 / 0.45 | 2884 | 9 |
| **all (pooled)** | 155 | 100 % | 2.4 / 7.4 | 0.25 / 0.42 | 3097 | 8 |
| **mean of sweep medians** | | | 2.4 | | | |
