# SCR anchors: bigclean-4XXA-plus4 on test_4XXA_run-405+run-406+run-407+run-408

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 2.0 / 6.9 | 0.21 / 0.42 | 2756 | 9 |
| run-406 | 39 | 100 % | 1.4 / 2.4 | 0.31 / 0.44 | 2569 | 10 |
| run-407 | 39 | 100 % | 2.2 / 4.1 | 0.20 / 0.44 | 2844 | 8 |
| run-408 | 39 | 100 % | 2.7 / 9.3 | 0.22 / 0.47 | 2398 | 11 |
| **all (pooled)** | 155 | 100 % | 2.1 / 6.0 | 0.25 / 0.45 | 2588 | 10 |
| **mean of sweep medians** | | | 2.1 | | | |
