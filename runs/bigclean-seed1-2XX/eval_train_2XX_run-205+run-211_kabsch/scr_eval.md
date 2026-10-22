# SCR anchors: bigclean-seed1-2XX on train_2XX_run-205+run-211_kabsch

One frame every 30 usable rows; 3D-3D RANSAC on the measured depth (20 mm, cells < 2000 mm, refine none, >= 30 inliers, seed 0 + row); camera position / rotation error against Polaris.

| sweep | frames | solved | error mm (median / p90) | error deg (median / p90) | inliers | ms |
|---|---|---|---|---|---|---|
| run-205 | 48 | 100 % | 4.5 / 8.1 | 0.29 / 0.46 | 1416 | 46 |
| run-211 | 29 | 100 % | 4.4 / 8.6 | 0.25 / 0.48 | 1191 | 45 |
| **all (pooled)** | 77 | 100 % | 4.4 / 8.5 | 0.27 / 0.48 | 1334 | 45 |
| **mean of sweep medians** | | | 4.4 | | | |
