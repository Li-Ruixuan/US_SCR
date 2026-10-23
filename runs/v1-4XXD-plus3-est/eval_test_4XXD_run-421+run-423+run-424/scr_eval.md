# SCR anchors: v1-4XXD-plus3-est on test_4XXD_run-421+run-423+run-424

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-421 | 39 | 100 % | 8.4 / 24.4 | 0.64 / 1.14 | 3079 | 8 |
| run-423 | 39 | 100 % | 8.7 / 27.8 | 0.65 / 1.12 | 2831 | 9 |
| run-424 | 39 | 100 % | 9.3 / 11.4 | 0.67 / 0.79 | 3109 | 8 |
| **all (pooled)** | 117 | 100 % | 9.1 / 17.8 | 0.67 / 0.95 | 2960 | 8 |
| **mean of sweep medians** | | | 8.8 | | | |
