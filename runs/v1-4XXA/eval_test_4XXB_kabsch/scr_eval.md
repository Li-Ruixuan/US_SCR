# SCR anchors: v1-4XXA on test_4XXB_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 10.7 / 14.3 | 0.35 / 0.45 | 1126 | 64 |
| run-410 | 38 | 100 % | 12.3 / 127.9 | 0.51 / 4.19 | 665 | 49 |
| run-411 | 38 | 100 % | 14.2 / 24.0 | 0.72 / 0.96 | 770 | 54 |
| run-412 | 39 | 100 % | 18.7 / 131.2 | 0.83 / 4.51 | 709 | 50 |
| **all (pooled)** | 155 | 100 % | 13.5 / 25.4 | 0.56 / 1.01 | 772 | 53 |
| **mean of sweep medians** | | | 14.0 | | | |
