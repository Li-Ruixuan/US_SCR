# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| track-v2-5XXA-exam | scr-track | 8 | 1.81 | **1.67** | 0.06 / **0.06** (0.2) | 0.35 / **0.25** (1.4) | 0.82 / **0.49** (5.4) |
| track-v2-5XXA-generic | scr-track | 8 | 10.93 | **3.93** | 0.09 / **0.07** (0.2) | 0.60 / **0.31** (1.4) | 1.71 / **0.68** (5.4) |
| track-v2map-5XXA-both | scr-track | 8 | 3.11 | **1.81** | 0.06 / **0.06** (0.2) | 0.35 / **0.26** (1.4) | 0.88 / **0.57** (5.4) |
| track-v2map-5XXA-exam-e20 | scr-track | 8 | 2.53 | **1.90** | 0.06 / **0.06** (0.2) | 0.39 / **0.25** (1.4) | 1.00 / **0.47** (5.4) |
| track-v2map-5XXA-exam-e40 | scr-track | 8 | 2.31 | **1.87** | 0.06 / **0.06** (0.2) | 0.36 / **0.25** (1.4) | 0.92 / **0.47** (5.4) |
| track-v2map-5XXA-exam-e80 | scr-track | 8 | 2.34 | **1.95** | 0.06 / **0.06** (0.2) | 0.35 / **0.26** (1.4) | 0.87 / **0.55** (5.4) |
