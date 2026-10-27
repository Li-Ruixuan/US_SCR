# U3: out-of-plane motion from per-patch speckle decorrelation (train_2XX)

759 pairs, patches 12 mm, curve built here, leave one sweep out. Out-of-plane error at the 5 US-image points (mm), over pairs. True motion in the header. 'fused': the system unless US differs by more than tau (mean over the points), then US.

| k (rows) | method | pairs | median | mean | p90 | p99 |
|---|---|---|---|---|---|---|
| **1** (true 0.3 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 248 | 0.22 | 0.29 | 0.55 | 1.24 |
| | system | 248 | 0.10 | 0.19 | 0.45 | 1.25 |
| | US, system sign | 248 | 0.27 | 0.33 | 0.61 | 1.40 |
| | fused, tau 1 mm | 248 | 0.10 | 0.19 | 0.47 | 1.33 |
| | fused, tau 2 mm | 248 | 0.10 | 0.18 | 0.45 | 1.14 |
| | fused, tau 3 mm | 248 | 0.10 | 0.19 | 0.45 | 1.25 |
| **4** (true 1.1 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 252 | 0.65 | 0.95 | 2.27 | 3.93 |
| | system | 252 | 0.44 | 0.70 | 1.57 | 4.18 |
| | US, system sign | 252 | 0.72 | 1.04 | 2.31 | 4.12 |
| | fused, tau 1 mm | 252 | 0.64 | 0.98 | 2.31 | 4.16 |
| | fused, tau 2 mm | 252 | 0.49 | 0.85 | 2.32 | 4.16 |
| | fused, tau 3 mm | 252 | 0.44 | 0.76 | 1.76 | 4.18 |
| **8** (true 2.4 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 259 | 1.27 | 2.07 | 4.96 | 8.67 |
| | system | 259 | 0.77 | 1.16 | 2.32 | 7.41 |
| | US, system sign | 259 | 1.45 | 2.20 | 4.96 | 8.67 |
| | fused, tau 1 mm | 259 | 1.45 | 2.15 | 4.96 | 8.67 |
| | fused, tau 2 mm | 259 | 1.20 | 2.05 | 4.96 | 8.67 |
| | fused, tau 3 mm | 259 | 0.96 | 1.92 | 4.96 | 8.67 |
