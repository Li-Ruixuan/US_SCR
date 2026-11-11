# Our system against ORB-SLAM3, paired by sweep (-occ30)

US-image error (mm): median per sweep, mean over sweeps; ours smoothed 1 s, ORB-SLAM3 1 s. Difference = ORB-SLAM3 - ours (negative: ORB-SLAM3 better), 95 % bootstrap interval over sweeps; p = Wilcoxon signed-rank (two-sided, >= 5 sweeps); 'ours lower' = sweeps where our error is lower; 'left out' = sweeps one system did not pose. `python tools/compare_stats.py` --modes online loc reloc --tag -occ30 --window 1.0

## ORB-SLAM3 online

| split | sweeps | ours | ORB-SLAM3 | difference [95 % CI] | p | ours lower | left out |
|---|---|---|---|---|---|---|---|
| 5XXB-exam | 8 | 5.16 | 1.76 | -3.40 [-3.88, -2.89] | 0.008 | 0 / 8 | 0 |
| 5XXC-exam | 8 | 3.54 | 2.12 | -1.42 [-2.35, -0.72] | 0.008 | 0 / 8 | 0 |

## ORB-SLAM3 loc

| split | sweeps | ours | ORB-SLAM3 | difference [95 % CI] | p | ours lower | left out |
|---|---|---|---|---|---|---|---|
| 5XXB-exam | 8 | 5.16 | 17.91 | 12.76 [-3.52, 44.86] | 0.195 | 1 / 8 | 0 |
| 5XXC-exam | 8 | 3.54 | 2.48 | -1.06 [-2.00, -0.33] | 0.039 | 1 / 8 | 0 |

## ORB-SLAM3 reloc

| split | sweeps | ours | ORB-SLAM3 | difference [95 % CI] | p | ours lower | left out |
|---|---|---|---|---|---|---|---|
| 5XXB-exam | 8 | 5.16 | 1.78 | -3.38 [-3.85, -2.90] | 0.008 | 0 / 8 | 0 |
| 5XXC-exam | 8 | 3.54 | 2.01 | -1.52 [-2.39, -0.88] | 0.008 | 0 / 8 | 0 |

