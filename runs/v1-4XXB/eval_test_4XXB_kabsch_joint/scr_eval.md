# SCR anchors: v1-4XXB on test_4XXB_kabsch_joint

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine joint, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-409 | 40 | 100 % | 6.4 / 10.1 | 0.35 / 0.62 | 2136 | 73 |
| run-410 | 38 | 100 % | 3.5 / 6.1 | 0.38 / 0.58 | 1269 | 56 |
| run-411 | 38 | 100 % | 4.8 / 8.1 | 0.29 / 0.51 | 1240 | 59 |
| run-412 | 39 | 100 % | 6.3 / 12.4 | 0.42 / 0.88 | 1122 | 56 |
| **all (pooled)** | 155 | 100 % | 5.6 / 10.3 | 0.37 / 0.68 | 1249 | 59 |
| **mean of sweep medians** | | | 5.3 | | | |
