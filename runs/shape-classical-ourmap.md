# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| 3XX | classical anchors + odometry | 5 | 3.65 | **2.66** | 0.10 / **0.07** (0.4) | 0.53 / **0.29** (3.0) | 1.39 / **0.59** (11.2) |
| 3XX | scr-track | 5 | 2.35 | **1.73** | 0.08 / **0.08** (0.4) | 0.45 / **0.36** (3.0) | 1.03 / **0.62** (11.2) |
