# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| 3XX | classical anchors + odometry | 5 | 3.11 | **2.47** | 0.09 / **0.07** (0.4) | 0.52 / **0.29** (3.0) | 1.32 / **0.62** (11.2) |
| 3XX | classical odometry only | 5 | 9.43 | **6.23** | 0.11 / **0.07** (0.4) | 0.61 / **0.28** (3.0) | 1.73 / **0.54** (11.2) |
| 3XX | scr-track | 5 | 1.85 | **1.57** | 0.08 / **0.08** (0.4) | 0.50 / **0.37** (3.0) | 1.07 / **0.62** (11.2) |
| 4XXA | classical anchors + odometry | 8 | 4.22 | **3.10** | 0.09 / **0.09** (0.3) | 0.48 / **0.34** (2.0) | 1.03 / **0.63** (7.6) |
| 4XXA | classical odometry only | 8 | 15.09 | **4.95** | 0.09 / **0.09** (0.3) | 0.45 / **0.33** (2.0) | 0.98 / **0.59** (7.6) |
| 4XXA | scr-track | 8 | 5.12 | **2.92** | 0.09 / **0.08** (0.3) | 0.53 / **0.36** (2.0) | 1.22 / **0.68** (7.6) |
| 4XXB | classical anchors + odometry | 4 | 3.38 | **2.47** | 0.09 / **0.08** (0.2) | 0.52 / **0.37** (1.8) | 1.25 / **0.67** (6.8) |
| 4XXB | classical odometry only | 4 | 11.28 | **6.58** | 0.10 / **0.08** (0.2) | 0.61 / **0.39** (1.8) | 1.73 / **0.78** (6.8) |
| 4XXB | scr-track | 4 | 5.77 | **2.66** | 0.08 / **0.07** (0.2) | 0.51 / **0.31** (1.8) | 1.22 / **0.59** (6.8) |
| 4XXC | classical anchors + odometry | 4 | 4.85 | **3.36** | 0.10 / **0.08** (0.2) | 0.54 / **0.38** (1.7) | 1.52 / **0.70** (6.5) |
| 4XXC | classical odometry only | 4 | 8.89 | **4.78** | 0.10 / **0.08** (0.2) | 0.57 / **0.40** (1.7) | 1.81 / **0.89** (6.5) |
| 4XXC | scr-track | 4 | 5.67 | **2.96** | 0.08 / **0.07** (0.2) | 0.46 / **0.31** (1.7) | 1.19 / **0.68** (6.5) |
| 4XXD | classical anchors + odometry | 6 | 6.32 | **3.61** | 0.11 / **0.08** (0.2) | 0.64 / **0.36** (1.8) | 1.83 / **0.76** (6.8) |
| 4XXD | classical odometry only | 6 | 12.74 | **8.36** | 0.12 / **0.09** (0.2) | 0.78 / **0.38** (1.8) | 2.52 / **0.85** (6.8) |
| 4XXD | scr-track | 6 | 9.63 | **3.16** | 0.11 / **0.09** (0.2) | 0.67 / **0.42** (1.8) | 1.73 / **0.76** (6.8) |
| 4XXE | classical anchors + odometry | 4 | 4.99 | **4.15** | 0.13 / **0.11** (0.3) | 0.73 / **0.51** (2.2) | 1.79 / **1.02** (8.5) |
| 4XXE | classical odometry only | 4 | 12.93 | **8.64** | 0.15 / **0.11** (0.3) | 0.92 / **0.54** (2.2) | 2.83 / **1.20** (8.5) |
| 4XXE | scr-track | 4 | 6.26 | **4.16** | 0.14 / **0.11** (0.3) | 0.84 / **0.57** (2.2) | 2.08 / **1.01** (8.5) |
