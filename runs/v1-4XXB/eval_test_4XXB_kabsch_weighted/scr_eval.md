# SCR anchors: v1-4XXB on test_4XXB_kabsch_weighted

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine weighted, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 7.7 / 11.0 | 0.48 / 0.77 | 2110 | 64 |
| run-410 | 38 | 100 % | 5.4 / 9.5 | 0.58 / 0.88 | 1264 | 49 |
| run-411 | 38 | 100 % | 6.7 / 10.1 | 0.55 / 0.73 | 1228 | 55 |
| run-412 | 39 | 100 % | 10.6 / 17.7 | 0.72 / 1.73 | 1102 | 50 |
| **all (pooled)** | 155 | 100 % | 7.0 / 13.7 | 0.58 / 0.98 | 1243 | 55 |
| **mean of sweep medians** | | | 7.6 | | | |
