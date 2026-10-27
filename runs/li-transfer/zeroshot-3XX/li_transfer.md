# Li et al. network on train_3XX: `runs/li-repro-M2/saved_model/best_validation_dist_model`, axes as-is

6 segments of 5 sweeps, new US frames only. Paper metrics, mean ± std over segments (mm); e_acc over every 4th pixel of the 640 × 480 image, all frames, relative to the segment's first frame.

| | e_frame | e_acc | e_drift | drift / path |
|---|---|---|---|---|
| **US network** | 0.82 ± 0.11 | 128.96 ± 64.26 | 278.45 ± 128.29 | 83.9 % |
| zero motion | 0.68 ± 0.17 | 57.80 ± 17.24 | 60.32 ± 38.90 | 27.5 % |

Relative motion between new US frames g apart (~19 frames/s), error at the 5 US-image points of anchoring.py (mm, median / mean / p90 over pairs): in-plane, **out-of-plane**; true out-of-plane motion in brackets.

| g | method | pairs | in-plane | **out-of-plane** |
|---|---|---|---|---|
| 1 (0.4 mm) | US network | 3043 | 0.33 / 0.40 / 0.72 | **0.43 / 0.61 / 1.35** |
| 1 (0.4 mm) | camera system | 3043 | 0.10 / 0.17 / 0.34 | **0.08 / 0.13 / 0.27** |
| 1 (0.4 mm) | zero motion | 3043 | 0.18 / 0.25 / 0.52 | **0.42 / 0.52 / 1.07** |
| 5 (2.3 mm) | US network | 3019 | 1.53 / 1.85 / 3.32 | **1.89 / 2.83 / 6.60** |
| 5 (2.3 mm) | camera system | 3019 | 0.40 / 0.64 / 1.28 | **0.22 / 0.38 / 0.80** |
| 5 (2.3 mm) | zero motion | 3019 | 0.90 / 1.16 / 2.24 | **2.27 / 2.56 / 4.72** |
| 19 (8.9 mm) | US network | 2935 | 5.35 / 6.43 / 11.97 | **6.43 / 10.08 / 24.47** |
| 19 (8.9 mm) | camera system | 2935 | 0.99 / 1.39 / 2.83 | **0.38 / 0.63 / 1.33** |
| 19 (8.9 mm) | zero motion | 2935 | 3.37 / 3.94 / 7.33 | **8.86 / 9.38 / 16.33** |
