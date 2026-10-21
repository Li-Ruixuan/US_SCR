# SCR anchors: v1-4XXC on test_4XXD

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-418 | 39 | 100 % | 11.9 / 18.0 | 0.85 / 1.07 | 1849 | 32 |
| run-419 | 39 | 100 % | 12.9 / 18.4 | 0.91 / 1.17 | 1842 | 27 |
| run-420 | 39 | 100 % | 21.6 / 42.0 | 1.31 / 1.98 | 1310 | 122 |
| run-421 | 39 | 100 % | 17.1 / 79.9 | 1.04 / 3.02 | 1285 | 134 |
| run-423 | 39 | 100 % | 15.5 / 37.3 | 1.06 / 1.89 | 1820 | 29 |
| run-424 | 39 | 100 % | 13.2 / 14.8 | 0.93 / 1.07 | 2138 | 15 |
| **all (pooled)** | 234 | 100 % | 14.4 / 29.2 | 0.98 / 1.54 | 1722 | 37 |
| **mean of sweep medians** | | | 15.4 | | | |
