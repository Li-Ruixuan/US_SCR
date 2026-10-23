# SCR anchors: v1-4XXA-plus1 on test_4XXA_run-405+run-406+run-407+run-408

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-405 | 38 | 100 % | 7.1 / 13.0 | 0.48 / 0.66 | 2736 | 9 |
| run-406 | 39 | 100 % | 1.9 / 4.6 | 0.34 / 0.44 | 2977 | 8 |
| run-407 | 39 | 100 % | 1.9 / 5.5 | 0.26 / 0.43 | 3025 | 8 |
| run-408 | 39 | 100 % | 2.9 / 10.1 | 0.28 / 0.53 | 2778 | 9 |
| **all (pooled)** | 155 | 100 % | 2.8 / 10.7 | 0.34 / 0.57 | 2920 | 9 |
| **mean of sweep medians** | | | 3.4 | | | |
