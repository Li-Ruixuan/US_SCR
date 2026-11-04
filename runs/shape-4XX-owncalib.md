# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| track-v2map-4XXC-owncalib | scr-track | 4 | 7.84 | **2.17** | 0.08 / **0.07** (0.2) | 0.41 / **0.29** (1.6) | 0.93 / **0.56** (6.4) |
| track-v2map-4XXD-owncalib | scr-track | 6 | 9.58 | **3.13** | 0.10 / **0.08** (0.2) | 0.62 / **0.39** (1.8) | 1.50 / **0.64** (6.6) |
