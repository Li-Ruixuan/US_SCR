# Our system against ORB-SLAM3, paired by sweep (-occ60)

US-image error (mm): median per sweep, mean over sweeps; ours smoothed 1 s, ORB-SLAM3 1 s. Difference = ORB-SLAM3 - ours (negative: ORB-SLAM3 better), 95 % bootstrap interval over sweeps; p = Wilcoxon signed-rank (two-sided, >= 5 sweeps); 'ours lower' = sweeps where our error is lower; 'left out' = sweeps one system did not pose. `python tools/compare_stats.py` --modes online loc reloc --tag -occ60 --window 1.0

## ORB-SLAM3 online

| split | sweeps | ours | ORB-SLAM3 | difference [95 % CI] | p | ours lower | left out |
|---|---|---|---|---|---|---|---|
| 5XXB-exam | 8 | 5.28 | 6.88 | 1.60 [-3.17, 10.67] | 0.195 | 1 / 8 | 0 |
| 5XXC-exam | 8 | 3.89 | 2.67 | -1.22 [-2.32, -0.31] | 0.039 | 1 / 8 | 0 |

## ORB-SLAM3 loc

| split | sweeps | ours | ORB-SLAM3 | difference [95 % CI] | p | ours lower | left out |
|---|---|---|---|---|---|---|---|
| 5XXB-exam | 8 | 5.28 | 3.32 | -1.96 [-3.09, -0.05] | 0.195 | 1 / 8 | 0 |
| 5XXC-exam | 8 | 3.89 | 2.65 | -1.23 [-2.29, -0.40] | 0.023 | 1 / 8 | 0 |

## ORB-SLAM3 reloc

| split | sweeps | ours | ORB-SLAM3 | difference [95 % CI] | p | ours lower | left out |
|---|---|---|---|---|---|---|---|
| 5XXB-exam | 8 | 5.28 | 6.72 | 1.44 [-3.85, 11.11] | 0.195 | 1 / 8 | 0 |
| 5XXC-exam | 3 | 3.63 | 2.22 | -1.41 [-2.70, -0.68] | – | 0 / 3 | 5 |

