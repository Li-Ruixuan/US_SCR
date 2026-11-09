# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| slam-4XXA-online | orbslam3 | 8 | 4.51 | **1.31** | 0.08 / **0.07** (0.2) | 0.34 / **0.25** (1.9) | 0.55 / **0.40** (7.4) |
| slam-4XXC-loc | orbslam3 | 1 | 4.22 | **1.21** | 0.06 / **0.06** (0.3) | 0.25 / **0.24** (2.2) | 0.38 / **0.33** (8.9) |
| slam-4XXC-online | orbslam3 | 2 | 11.72 | **13.72** | 0.07 / **0.09** (0.2) | 0.33 / **0.38** (1.9) | 0.64 / **0.82** (8.0) |
| slam-4XXD-online | orbslam3 | 6 | 4.69 | **1.16** | 0.07 / **0.07** (0.2) | 0.26 / **0.24** (1.8) | 0.46 / **0.36** (6.6) |
| slam-4XXE-online | orbslam3 | 4 | 4.39 | **1.54** | 0.09 / **0.09** (0.3) | 0.39 / **0.32** (2.2) | 0.67 / **0.45** (8.4) |
| slam-5XXA-exam-loc | orbslam3 | 2 | 40.10 | **20.24** | 0.07 / **0.13** (0.2) | 0.43 / **0.96** (1.5) | 1.17 / **3.36** (5.6) |
| slam-5XXA-exam-online | orbslam3 | 8 | 3.52 | **1.11** | 0.05 / **0.06** (0.2) | 0.24 / **0.21** (1.4) | 0.47 / **0.33** (5.4) |
| slam-5XXB-exam-online | orbslam3 | 8 | 1.79 | **1.22** | 0.05 / **0.06** (0.2) | 0.22 / **0.21** (1.8) | 0.44 / **0.40** (6.8) |
| slam-5XXC-exam-loc | orbslam3 | 1 | 51.07 | **35.62** | 0.04 / **0.19** (0.2) | 0.28 / **1.54** (1.5) | 0.92 / **5.68** (5.5) |
| slam-5XXC-exam-online | orbslam3 | 8 | 1.67 | **1.09** | 0.04 / **0.06** (0.2) | 0.22 / **0.20** (1.7) | 0.40 / **0.37** (6.5) |
| slam-5XXC-oldB-loc | orbslam3 | 5 | 335.83 | **102.35** | 0.05 / **0.07** (0.2) | 0.29 / **0.42** (1.6) | 0.80 / **1.41** (5.9) |
| slam-5XXC-oldB-online | orbslam3 | 8 | 43.69 | **3.51** | 0.04 / **0.06** (0.2) | 0.19 / **0.19** (1.7) | 0.40 / **0.37** (6.5) |
| slam-5XXD-exam-loc | orbslam3 | 2 | 30.41 | **24.05** | 0.07 / **0.13** (0.2) | 0.38 / **0.87** (1.5) | 0.97 / **3.02** (5.8) |
| slam-5XXD-exam-online | orbslam3 | 4 | 1.53 | **1.17** | 0.07 / **0.08** (0.2) | 0.36 / **0.32** (1.9) | 0.60 / **0.52** (7.0) |
| slam-5XXE-exam-loc | orbslam3 | 1 | 1.55 | **0.78** | 0.04 / **0.06** (0.2) | 0.21 / **0.21** (1.6) | 0.39 / **0.42** (6.0) |
| slam-5XXE-exam-online | orbslam3 | 4 | 2.23 | **0.79** | 0.04 / **0.06** (0.2) | 0.17 / **0.18** (1.6) | 0.32 / **0.29** (6.1) |
| slam-5XXE-oldC-online | orbslam3 | 4 | 2.82 | **1.08** | 0.04 / **0.06** (0.2) | 0.18 / **0.19** (1.6) | 0.34 / **0.32** (6.1) |
