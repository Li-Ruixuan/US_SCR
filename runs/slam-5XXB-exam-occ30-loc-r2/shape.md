# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| slam-5XXB-exam-occ30-loc-r2 | orbslam3 | 8 | 17.39 | **6.35** | 0.05 / **0.07** (0.2) | 0.27 / **0.30** (1.8) | 0.68 / **0.64** (6.8) |
