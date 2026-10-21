# SCR anchors: v1-4XXA on test_4XXC

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 39.8 / 52.3 | 1.02 / 1.56 | 654 | 221 |
| run-414 | 39 | 100 % | 47.5 / 65.7 | 1.66 / 2.49 | 526 | 220 |
| run-415 | 39 | 100 % | 50.2 / 64.9 | 1.47 / 1.94 | 842 | 223 |
| run-416 | 39 | 100 % | 52.2 / 75.8 | 1.42 / 2.82 | 813 | 223 |
| **all (pooled)** | 155 | 100 % | 46.0 / 65.2 | 1.44 / 2.19 | 690 | 221 |
| **mean of sweep medians** | | | 47.4 | | | |
