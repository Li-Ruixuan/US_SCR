# SCR anchors: v1-4XXA on test_4XXA_kabsch_joint

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine joint, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-401 | 58 | 100 % | 6.1 / 9.4 | 0.39 / 0.59 | 1954 | 69 |
| run-402 | 37 | 100 % | 7.7 / 10.1 | 0.60 / 0.72 | 1943 | 77 |
| run-403 | 59 | 100 % | 6.8 / 9.0 | 0.48 / 0.71 | 1790 | 67 |
| run-404 | 39 | 100 % | 10.6 / 14.0 | 0.71 / 1.05 | 1574 | 70 |
| run-405 | 38 | 100 % | 8.3 / 13.7 | 0.56 / 0.82 | 1434 | 65 |
| run-406 | 39 | 100 % | 4.9 / 8.2 | 0.37 / 0.51 | 1765 | 59 |
| run-407 | 39 | 100 % | 5.7 / 11.6 | 0.46 / 0.80 | 1842 | 64 |
| run-408 | 39 | 100 % | 7.9 / 12.0 | 0.60 / 0.86 | 1517 | 58 |
| **all (pooled)** | 348 | 100 % | 7.4 / 11.3 | 0.51 / 0.78 | 1776 | 65 |
| **mean of sweep medians** | | | 7.3 | | | |
