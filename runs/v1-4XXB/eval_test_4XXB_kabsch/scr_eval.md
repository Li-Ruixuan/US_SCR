# SCR anchors: v1-4XXB on test_4XXB_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 6.3 / 7.5 | 0.36 / 0.44 | 2142 | 63 |
| run-410 | 38 | 100 % | 4.8 / 7.2 | 0.43 / 0.60 | 1289 | 49 |
| run-411 | 38 | 100 % | 5.3 / 7.9 | 0.39 / 0.54 | 1237 | 54 |
| run-412 | 39 | 100 % | 6.9 / 11.7 | 0.44 / 0.89 | 1153 | 49 |
| **all (pooled)** | 155 | 100 % | 5.9 / 9.2 | 0.40 / 0.64 | 1267 | 52 |
| **mean of sweep medians** | | | 5.9 | | | |
