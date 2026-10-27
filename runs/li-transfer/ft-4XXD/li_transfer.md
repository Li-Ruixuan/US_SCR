# Li et al. network on test_4XXD: `runs/li-transfer/ft-2XX/saved_model/best_model`, axes as-is

6 segments of 6 sweeps, new US frames only. Paper metrics, mean ± std over segments (mm); e_acc over every 4th pixel of the 640 × 480 image, all frames, relative to the segment's first frame.

| | e_frame | e_acc | e_drift | drift / path |
|---|---|---|---|---|
| **US network** | 0.67 ± 0.07 | 81.73 ± 16.33 | 164.52 ± 47.45 | 45.5 % |
| zero motion | 0.49 ± 0.09 | 53.26 ± 16.13 | 16.85 ± 2.95 | 4.6 % |

Relative motion between new US frames g apart (~19 frames/s), error at the 5 US-image points of anchoring.py (mm, median / mean / p90 over pairs): in-plane, **out-of-plane**; true out-of-plane motion in brackets.

| g | method | pairs | in-plane | **out-of-plane** |
|---|---|---|---|---|
| 1 (0.3 mm) | US network | 5168 | 0.22 / 0.28 / 0.52 | **0.38 / 0.49 / 1.02** |
| 1 (0.3 mm) | camera system | 5168 | 0.12 / 0.19 / 0.40 | **0.09 / 0.14 / 0.32** |
| 1 (0.3 mm) | zero motion | 5168 | 0.13 / 0.20 / 0.44 | **0.28 / 0.36 / 0.74** |
| 5 (1.5 mm) | US network | 5144 | 0.98 / 1.20 / 2.23 | **1.79 / 2.25 / 4.69** |
| 5 (1.5 mm) | camera system | 5144 | 0.50 / 0.73 / 1.55 | **0.30 / 0.47 / 1.08** |
| 5 (1.5 mm) | zero motion | 5144 | 0.61 / 0.86 / 1.87 | **1.48 / 1.70 / 3.50** |
| 19 (5.8 mm) | US network | 5060 | 3.38 / 3.97 / 7.34 | **6.79 / 8.05 / 16.54** |
| 19 (5.8 mm) | camera system | 5060 | 1.37 / 1.97 / 4.39 | **0.61 / 0.96 / 2.38** |
| 19 (5.8 mm) | zero motion | 5060 | 2.13 / 2.76 / 5.77 | **5.79 / 6.18 / 12.19** |
