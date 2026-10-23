# SCR anchors: v1-4XXA-plus2-est on test_4XXA_run-405+run-406+run-407+run-408

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 7.6 / 13.3 | 0.53 / 0.89 | 2886 | 9 |
| run-406 | 39 | 100 % | 3.8 / 8.3 | 0.39 / 0.49 | 3008 | 8 |
| run-407 | 39 | 100 % | 4.1 / 8.1 | 0.53 / 0.67 | 3145 | 8 |
| run-408 | 39 | 100 % | 5.3 / 10.3 | 0.59 / 0.75 | 2838 | 9 |
| **all (pooled)** | 155 | 100 % | 5.4 / 11.7 | 0.51 / 0.73 | 2964 | 8 |
| **mean of sweep medians** | | | 5.2 | | | |
