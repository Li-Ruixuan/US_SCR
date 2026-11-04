# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| track-v2map-pool-4XXB | scr-track | 4 | 8.08 | **2.53** | 0.07 / **0.07** (0.2) | 0.37 / **0.31** (1.7) | 0.78 / **0.52** (6.5) |
| track-v2map-pool-4XXC | scr-track | 4 | 10.69 | **2.21** | 0.07 / **0.06** (0.2) | 0.38 / **0.27** (1.6) | 0.78 / **0.55** (6.4) |
| track-v2map-pool-4XXD | scr-track | 6 | 14.00 | **3.98** | 0.10 / **0.09** (0.2) | 0.62 / **0.42** (1.8) | 1.51 / **0.73** (6.6) |
| track-v2map-pool-4XXE | scr-track | 4 | 10.62 | **3.15** | 0.13 / **0.10** (0.3) | 0.73 / **0.50** (2.2) | 1.77 / **0.83** (8.4) |
