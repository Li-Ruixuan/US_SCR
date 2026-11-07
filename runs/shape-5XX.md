# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| track-v2map-5XXA-after | scr-track | 8 | 2.48 | **1.96** | 0.06 / **0.06** (0.2) | 0.36 / **0.26** (1.4) | 0.94 / **0.54** (5.4) |
| track-v2map-5XXA-exam | scr-track | 8 | 2.26 | **1.90** | 0.06 / **0.06** (0.2) | 0.34 / **0.27** (1.4) | 0.86 / **0.56** (5.4) |
| track-v2map-5XXA-generic | scr-track | 8 | 13.57 | **3.79** | 0.08 / **0.07** (0.2) | 0.59 / **0.30** (1.4) | 1.70 / **0.70** (5.4) |
| track-v2map-5XXB-exam | scr-track | 8 | 4.41 | **2.81** | 0.06 / **0.07** (0.2) | 0.37 / **0.28** (1.8) | 1.03 / **0.62** (6.8) |
| track-v2map-5XXB-generic | scr-track | 8 | 3.35 | **2.46** | 0.06 / **0.07** (0.2) | 0.35 / **0.26** (1.8) | 0.97 / **0.53** (6.8) |
| track-v2map-5XXB-oldA | scr-track | 8 | 4.23 | **3.00** | 0.09 / **0.07** (0.2) | 0.61 / **0.32** (1.8) | 1.57 / **0.69** (6.8) |
| track-v2map-5XXC-exam | scr-track | 8 | 3.09 | **1.76** | 0.04 / **0.06** (0.2) | 0.23 / **0.20** (1.7) | 0.62 / **0.36** (6.5) |
| track-v2map-5XXC-generic | scr-track | 8 | 6.32 | **1.76** | 0.04 / **0.06** (0.2) | 0.23 / **0.22** (1.7) | 0.64 / **0.46** (6.5) |
| track-v2map-5XXC-oldA | scr-track | 2 | 58.59 | **47.65** | 0.08 / **0.18** (0.2) | 0.57 / **1.48** (1.9) | 1.79 / **5.32** (7.3) |
| track-v2map-5XXC-oldB | scr-track | 8 | 40.70 | **29.24** | 0.07 / **0.17** (0.2) | 0.47 / **1.36** (1.7) | 1.53 / **5.03** (6.5) |
| track-v2map-5XXD-exam | scr-track | 4 | 2.19 | **1.70** | 0.06 / **0.08** (0.2) | 0.35 / **0.34** (1.9) | 0.73 / **0.57** (7.0) |
| track-v2map-5XXD-generic | scr-track | 4 | 5.09 | **1.28** | 0.06 / **0.08** (0.2) | 0.33 / **0.35** (1.9) | 0.65 / **0.58** (7.0) |
| track-v2map-5XXE-exam | scr-track | 4 | 5.86 | **3.04** | 0.04 / **0.06** (0.2) | 0.28 / **0.25** (1.6) | 0.79 / **0.63** (6.1) |
| track-v2map-5XXE-generic | scr-track | 4 | 13.08 | **2.83** | 0.04 / **0.06** (0.2) | 0.28 / **0.25** (1.6) | 0.81 / **0.56** (6.1) |
| track-v2map-5XXE-oldC | scr-track | 4 | 13.61 | **14.61** | 0.08 / **0.13** (0.2) | 0.55 / **0.94** (1.6) | 1.84 / **3.24** (6.1) |
