# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| 3XX | classical anchors + odometry | 5 | 3.65 | **2.66** | 0.10 / **0.07** (0.4) | 0.53 / **0.29** (3.0) | 1.39 / **0.59** (11.2) |
| 3XX | scr-track | 5 | 2.35 | **1.73** | 0.08 / **0.08** (0.4) | 0.45 / **0.36** (3.0) | 1.03 / **0.62** (11.2) |
| 4XXA | classical anchors + odometry | 8 | 6.49 | **4.27** | 0.11 / **0.09** (0.3) | 0.58 / **0.34** (2.0) | 1.52 / **0.61** (7.6) |
| 4XXA | scr-track | 8 | 4.99 | **2.99** | 0.09 / **0.08** (0.3) | 0.52 / **0.36** (2.0) | 1.21 / **0.63** (7.6) |
| 4XXB | classical anchors + odometry | 4 | 4.27 | **2.58** | 0.10 / **0.08** (0.2) | 0.53 / **0.37** (1.8) | 1.29 / **0.67** (6.8) |
| 4XXB | scr-track | 4 | 6.55 | **2.41** | 0.08 / **0.07** (0.2) | 0.43 / **0.31** (1.8) | 0.92 / **0.53** (6.8) |
| 4XXC | classical anchors + odometry | 4 | 4.94 | **3.75** | 0.10 / **0.08** (0.2) | 0.55 / **0.37** (1.7) | 1.54 / **0.71** (6.5) |
| 4XXC | scr-track | 4 | 9.41 | **2.12** | 0.08 / **0.07** (0.2) | 0.43 / **0.28** (1.7) | 0.94 / **0.56** (6.5) |
| 4XXD | classical anchors + odometry | 6 | 7.41 | **4.32** | 0.11 / **0.08** (0.2) | 0.65 / **0.37** (1.8) | 1.90 / **0.76** (6.8) |
| 4XXD | scr-track | 6 | 11.59 | **3.09** | 0.11 / **0.09** (0.2) | 0.63 / **0.41** (1.8) | 1.57 / **0.68** (6.8) |
| 4XXE | classical anchors + odometry | 4 | 5.60 | **4.53** | 0.14 / **0.11** (0.3) | 0.75 / **0.52** (2.2) | 1.86 / **1.01** (8.5) |
| 4XXE | scr-track | 4 | 7.09 | **3.05** | 0.13 / **0.10** (0.3) | 0.76 / **0.54** (2.2) | 1.86 / **0.83** (8.5) |
