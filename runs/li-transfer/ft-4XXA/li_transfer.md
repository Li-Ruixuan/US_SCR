# Li et al. network on test_4XXA: `runs/li-transfer/ft-2XX/saved_model/best_model`, axes as-is

8 segments of 8 sweeps, new US frames only. Paper metrics, mean ± std over segments (mm); e_acc over every 4th pixel of the 640 × 480 image, all frames, relative to the segment's first frame.

| | e_frame | e_acc | e_drift | drift / path |
|---|---|---|---|---|
| **US network** | 0.74 ± 0.12 | 125.43 ± 32.89 | 174.73 ± 71.37 | 41.3 % |
| zero motion | 0.52 ± 0.16 | 49.33 ± 13.67 | 34.22 ± 32.42 | 7.5 % |

Relative motion between new US frames g apart (~19 frames/s), error at the 5 US-image points of anchoring.py (mm, median / mean / p90 over pairs): in-plane, **out-of-plane**; true out-of-plane motion in brackets.

| g | method | pairs | in-plane | **out-of-plane** |
|---|---|---|---|---|
| 1 (0.3 mm) | US network | 7718 | 0.22 / 0.31 / 0.63 | **0.44 / 0.57 / 1.19** |
| 1 (0.3 mm) | camera system | 7718 | 0.11 / 0.17 / 0.34 | **0.10 / 0.16 / 0.35** |
| 1 (0.3 mm) | zero motion | 7718 | 0.16 / 0.24 / 0.54 | **0.28 / 0.41 / 0.91** |
| 5 (1.5 mm) | US network | 7686 | 1.04 / 1.39 / 2.78 | **2.14 / 2.66 / 5.54** |
| 5 (1.5 mm) | camera system | 7686 | 0.38 / 0.59 / 1.18 | **0.28 / 0.51 / 1.11** |
| 5 (1.5 mm) | zero motion | 7686 | 0.79 / 1.10 / 2.45 | **1.54 / 1.96 / 4.33** |
| 19 (6.2 mm) | US network | 7574 | 3.71 / 4.70 / 9.61 | **7.94 / 9.59 / 19.82** |
| 19 (6.2 mm) | camera system | 7574 | 0.77 / 1.13 / 2.37 | **0.49 / 0.83 / 1.93** |
| 19 (6.2 mm) | zero motion | 7574 | 2.82 / 3.73 / 8.44 | **6.22 / 7.23 / 16.27** |
