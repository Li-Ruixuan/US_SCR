# SCR anchors: v1-4XXA on test_4XXC_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-413 | 38 | 100 % | 11.6 / 108.6 | 1.12 / 3.83 | 429 | 62 |
| run-414 | 39 | 100 % | 12.9 / 130.0 | 2.30 / 4.20 | 410 | 60 |
| run-415 | 39 | 100 % | 14.6 / 88.6 | 1.15 / 2.84 | 365 | 59 |
| run-416 | 39 | 100 % | 14.3 / 109.3 | 1.02 / 3.80 | 328 | 60 |
| **all (pooled)** | 155 | 100 % | 13.4 / 113.0 | 1.30 / 3.85 | 396 | 60 |
| **mean of sweep medians** | | | 13.4 | | | |
