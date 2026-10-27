# Li et al. network on train_2XX: `runs/li-repro-M2/saved_model/best_validation_dist_model`, axes as-is

2 segments of 2 sweeps, new US frames only. Paper metrics, mean ± std over segments (mm); e_acc over every 4th pixel of the 640 × 480 image, all frames, relative to the segment's first frame.

| | e_frame | e_acc | e_drift | drift / path |
|---|---|---|---|---|
| **US network** | 0.86 ± 0.10 | 199.33 ± 43.58 | 410.05 ± 45.37 | 118.6 % |
| zero motion | 0.52 ± 0.13 | 31.89 ± 4.67 | 19.93 ± 6.41 | 5.1 % |

Relative motion between new US frames g apart (~19 frames/s), error at the 5 US-image points of anchoring.py (mm, median / mean / p90 over pairs): in-plane, **out-of-plane**; true out-of-plane motion in brackets.

| g | method | pairs | in-plane | **out-of-plane** |
|---|---|---|---|---|
| 1 (0.3 mm) | US network | 1748 | 0.40 / 0.44 / 0.71 | **0.52 / 0.66 / 1.35** |
| 1 (0.3 mm) | zero motion | 1748 | 0.12 / 0.18 / 0.34 | **0.34 / 0.47 / 1.04** |
| 5 (1.8 mm) | US network | 1740 | 1.94 / 2.07 / 3.28 | **2.66 / 3.16 / 6.33** |
| 5 (1.8 mm) | zero motion | 1740 | 0.59 / 0.78 / 1.41 | **1.85 / 2.29 / 4.78** |
| 19 (7.4 mm) | US network | 1712 | 6.69 / 7.13 / 11.49 | **10.05 / 11.60 / 23.10** |
| 19 (7.4 mm) | zero motion | 1712 | 2.11 / 2.49 / 4.38 | **7.43 / 8.35 / 17.55** |
