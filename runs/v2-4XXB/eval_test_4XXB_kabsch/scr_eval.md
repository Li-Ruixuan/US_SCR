# SCR anchors: v2-4XXB on test_4XXB_kabsch

One frame every 30 usable rows; Kabsch RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 6.1 / 7.1 | 0.35 / 0.45 | 2194 | 65 |
| run-410 | 38 | 100 % | 5.6 / 8.1 | 0.42 / 0.54 | 1337 | 52 |
| run-411 | 38 | 100 % | 4.0 / 5.8 | 0.30 / 0.47 | 1330 | 55 |
| run-412 | 39 | 100 % | 6.9 / 9.2 | 0.41 / 0.56 | 1246 | 52 |
| **all (pooled)** | 155 | 100 % | 5.8 / 8.0 | 0.35 / 0.52 | 1375 | 54 |
| **mean of sweep medians** | | | 5.6 | | | |
