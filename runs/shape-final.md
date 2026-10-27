# Shape of the reconstruction: absolute, after a rigid fit, and between nearby frames

Error at the 5 US-image points (mm), median per sweep, mean over sweeps. **shape** = after the best rigid fit of the whole sweep to Polaris. Relative error for frames k rows apart (30 rows = 1 s): in-plane / **out-of-plane**, true out-of-plane motion in brackets.

| split | source | sweeps | absolute | **shape** | k = 1: in / **out** (true) | k = 8: in / **out** (true) | k = 30: in / **out** (true) |
|---|---|---|---|---|---|---|---|
| 2XX | SCR anchors + odometry | 2 | 4.19 | **3.32** | 0.14 / **0.13** (0.3) | 0.83 / **0.73** (2.6) | 1.85 / **1.32** (9.5) |
| 2XX | classical anchors + odometry | 2 | 4.22 | **3.98** | 0.15 / **0.13** (0.3) | 0.89 / **0.75** (2.6) | 1.99 / **1.42** (9.5) |
| 2XX | classical odometry only | 2 | 36.98 | **14.26** | 0.14 / **0.12** (0.3) | 0.85 / **0.69** (2.6) | 1.94 / **1.44** (9.5) |
| 3XX | SCR anchors + odometry | 5 | 2.54 | **2.07** | 0.09 / **0.07** (0.4) | 0.50 / **0.27** (3.0) | 1.34 / **0.47** (11.2) |
| 3XX | classical anchors + odometry | 5 | 3.11 | **2.47** | 0.09 / **0.07** (0.4) | 0.52 / **0.29** (3.0) | 1.32 / **0.62** (11.2) |
| 3XX | classical odometry only | 5 | 9.43 | **6.23** | 0.11 / **0.07** (0.4) | 0.61 / **0.28** (3.0) | 1.73 / **0.54** (11.2) |
| 4XXA | SCR anchors + odometry | 8 | 4.97 | **2.65** | 0.09 / **0.09** (0.3) | 0.46 / **0.33** (2.0) | 0.94 / **0.56** (7.6) |
| 4XXA | classical anchors + odometry | 8 | 4.22 | **3.10** | 0.09 / **0.09** (0.3) | 0.48 / **0.34** (2.0) | 1.03 / **0.63** (7.6) |
| 4XXA | classical odometry only | 8 | 15.09 | **4.95** | 0.09 / **0.09** (0.3) | 0.45 / **0.33** (2.0) | 0.98 / **0.59** (7.6) |
| 4XXB | SCR anchors + odometry | 4 | 5.72 | **3.23** | 0.09 / **0.08** (0.2) | 0.53 / **0.37** (1.8) | 1.27 / **0.70** (6.8) |
| 4XXB | classical anchors + odometry | 4 | 3.38 | **2.47** | 0.09 / **0.08** (0.2) | 0.52 / **0.37** (1.8) | 1.25 / **0.67** (6.8) |
| 4XXB | classical odometry only | 4 | 11.28 | **6.58** | 0.10 / **0.08** (0.2) | 0.61 / **0.39** (1.8) | 1.73 / **0.78** (6.8) |
| 4XXC | SCR anchors + odometry | 4 | 5.90 | **3.24** | 0.09 / **0.08** (0.2) | 0.50 / **0.37** (1.7) | 1.29 / **0.75** (6.5) |
| 4XXC | classical anchors + odometry | 4 | 4.85 | **3.36** | 0.10 / **0.08** (0.2) | 0.54 / **0.38** (1.7) | 1.52 / **0.70** (6.5) |
| 4XXC | classical odometry only | 4 | 8.89 | **4.78** | 0.10 / **0.08** (0.2) | 0.57 / **0.40** (1.7) | 1.81 / **0.89** (6.5) |
| 4XXD | SCR anchors + odometry | 6 | 9.63 | **3.77** | 0.11 / **0.08** (0.2) | 0.65 / **0.35** (1.8) | 1.85 / **0.77** (6.8) |
| 4XXD | classical anchors + odometry | 6 | 6.32 | **3.61** | 0.11 / **0.08** (0.2) | 0.64 / **0.36** (1.8) | 1.83 / **0.76** (6.8) |
| 4XXD | classical odometry only | 6 | 12.74 | **8.36** | 0.12 / **0.09** (0.2) | 0.78 / **0.38** (1.8) | 2.52 / **0.85** (6.8) |
| 4XXE | SCR anchors + odometry | 4 | 6.48 | **4.75** | 0.15 / **0.11** (0.3) | 0.85 / **0.52** (2.2) | 2.47 / **1.06** (8.5) |
| 4XXE | classical anchors + odometry | 4 | 4.99 | **4.15** | 0.13 / **0.11** (0.3) | 0.73 / **0.51** (2.2) | 1.79 / **1.02** (8.5) |
| 4XXE | classical odometry only | 4 | 12.93 | **8.64** | 0.15 / **0.11** (0.3) | 0.92 / **0.54** (2.2) | 2.83 / **1.20** (8.5) |
