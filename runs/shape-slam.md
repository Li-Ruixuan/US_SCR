# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| slam-3XX | orbslam3 | 5 | 1.79 | **1.34** | 0.08 / **0.07** (0.4) | 0.43 / **0.25** (3.0) | 0.83 / **0.45** (11.2) |
| slam-5XXA-exam | orbslam3 | 8 | 16.70 | **2.32** | 0.05 / **0.06** (0.2) | 0.29 / **0.23** (1.4) | 0.65 / **0.49** (5.4) |
