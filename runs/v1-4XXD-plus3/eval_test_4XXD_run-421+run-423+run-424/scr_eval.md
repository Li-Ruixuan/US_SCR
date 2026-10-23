# SCR anchors: v1-4XXD-plus3 on test_4XXD_run-421+run-423+run-424

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-421 | 39 | 100 % | 2.1 / 9.0 | 0.15 / 0.54 | 3041 | 8 |
| run-423 | 39 | 100 % | 5.0 / 15.9 | 0.45 / 0.57 | 2890 | 9 |
| run-424 | 39 | 100 % | 4.1 / 5.9 | 0.20 / 0.38 | 3055 | 8 |
| **all (pooled)** | 117 | 100 % | 4.1 / 8.9 | 0.26 / 0.50 | 2972 | 8 |
| **mean of sweep medians** | | | 3.7 | | | |
