# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| 3XX | classical anchors + odometry | 5 | 3.11 | **2.47** | 0.09 / **0.07** (0.4) | 0.52 / **0.29** (3.0) | 1.32 / **0.62** (11.2) |
| 3XX | classical odometry only | 5 | 9.43 | **6.23** | 0.11 / **0.07** (0.4) | 0.61 / **0.28** (3.0) | 1.73 / **0.54** (11.2) |
| 3XX | scr-track | 5 | 12.49 | **4.74** | 0.10 / **0.08** (0.4) | 0.58 / **0.46** (3.0) | 1.52 / **1.24** (11.2) |
