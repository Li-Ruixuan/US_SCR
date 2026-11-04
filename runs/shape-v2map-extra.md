# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| track-v2map-2XX | scr-track | 2 | 8.06 | **6.93** | 0.13 / **0.10** (0.3) | 0.91 / **0.53** (2.5) | 2.39 / **1.33** (9.3) |
| track-v2map-3XX-room301 | scr-track | 3 | 2.94 | **2.18** | 0.10 / **0.09** (0.4) | 0.62 / **0.43** (3.3) | 1.50 / **0.80** (12.1) |
| track-v2map-3XX-seed1 | scr-track | 5 | 2.20 | **1.75** | 0.08 / **0.08** (0.4) | 0.47 / **0.37** (3.0) | 1.06 / **0.66** (11.2) |
| track-v2map-3XX-seed2 | scr-track | 5 | 2.24 | **1.70** | 0.08 / **0.08** (0.4) | 0.47 / **0.38** (3.0) | 1.07 / **0.68** (11.2) |
