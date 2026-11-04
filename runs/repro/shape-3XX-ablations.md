# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| track-v2map-3XX-nocalib | scr-track | 5 | 11.49 | **4.08** | 0.09 / **0.09** (0.4) | 0.54 / **0.48** (3.0) | 1.37 / **1.18** (11.2) |
| track-v2map-3XX-noloops | scr-track | 5 | 5.77 | **3.18** | 0.10 / **0.08** (0.4) | 0.60 / **0.40** (3.0) | 1.61 / **0.70** (11.2) |
