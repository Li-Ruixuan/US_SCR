# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| slam-3XX | orbslam3 | 5 | 1.79 | **1.34** | 0.08 / **0.07** (0.4) | 0.43 / **0.25** (3.0) | 0.83 / **0.45** (11.2) |
| slam-4XXA | orbslam3 | 8 | 4.45 | **1.45** | 0.08 / **0.08** (0.2) | 0.38 / **0.29** (1.9) | 0.64 / **0.45** (7.4) |
| slam-4XXB | orbslam3 | 4 | 2.99 | **1.11** | 0.07 / **0.07** (0.2) | 0.35 / **0.28** (1.7) | 0.62 / **0.47** (6.5) |
| slam-4XXC | orbslam3 | 4 | 3.63 | **1.20** | 0.06 / **0.06** (0.2) | 0.27 / **0.26** (1.6) | 0.46 / **0.44** (6.4) |
| slam-4XXD | orbslam3 | 6 | 3.63 | **1.28** | 0.07 / **0.07** (0.2) | 0.28 / **0.25** (1.8) | 0.47 / **0.39** (6.6) |
| slam-4XXE | orbslam3 | 4 | 3.04 | **1.43** | 0.10 / **0.08** (0.3) | 0.42 / **0.32** (2.2) | 0.73 / **0.47** (8.4) |
| slam-5XXA-exam | orbslam3 | 8 | 3.29 | **1.15** | 0.05 / **0.06** (0.2) | 0.26 / **0.20** (1.4) | 0.50 / **0.31** (5.4) |
| slam-5XXB-exam | orbslam3 | 8 | 1.79 | **1.25** | 0.05 / **0.06** (0.2) | 0.24 / **0.24** (1.8) | 0.48 / **0.43** (6.8) |
| slam-5XXC-exam | orbslam3 | 8 | 1.88 | **1.17** | 0.05 / **0.06** (0.2) | 0.26 / **0.21** (1.7) | 0.52 / **0.38** (6.5) |
| slam-5XXC-oldB | orbslam3 | 8 | 4.65 | **1.15** | 0.04 / **0.06** (0.2) | 0.20 / **0.19** (1.7) | 0.41 / **0.37** (6.5) |
| slam-5XXD-exam | orbslam3 | 4 | 2.11 | **1.21** | 0.07 / **0.08** (0.2) | 0.37 / **0.34** (1.9) | 0.60 / **0.52** (7.0) |
| slam-5XXE-exam | orbslam3 | 4 | 2.56 | **0.77** | 0.04 / **0.06** (0.2) | 0.18 / **0.19** (1.6) | 0.33 / **0.32** (6.1) |
| slam-5XXE-oldC | orbslam3 | 4 | 3.06 | **0.85** | 0.04 / **0.06** (0.2) | 0.18 / **0.21** (1.6) | 0.33 / **0.33** (6.1) |
