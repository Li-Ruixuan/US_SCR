# SCR anchors: v1-4XXB on test_4XXB

One frame every 30 usable rows; PnP-RANSAC (10 px, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 8.1 / 12.7 | 0.46 / 0.53 | 2738 | 10 |
| run-410 | 38 | 100 % | 8.2 / 16.7 | 0.50 / 0.70 | 1710 | 37 |
| run-411 | 38 | 100 % | 7.7 / 11.4 | 0.45 / 0.68 | 1820 | 28 |
| run-412 | 39 | 100 % | 10.6 / 21.6 | 0.64 / 1.05 | 1164 | 216 |
| **all (pooled)** | 155 | 100 % | 8.7 / 17.8 | 0.48 / 0.83 | 1798 | 29 |
| **mean of sweep medians** | | | 8.6 | | | |
