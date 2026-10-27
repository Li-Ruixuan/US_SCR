# U3: out-of-plane motion from per-patch speckle decorrelation (train_3XX)

1400 pairs, patches 12 mm, curve from /data2/u0137815/rgbd-us/data/train_2XX. Out-of-plane error at the 5 US-image points (mm), over pairs. True motion in the header. 'fused': the system unless US differs by more than tau (mean over the points), then US.

| k (rows) | method | pairs | median | mean | p90 | p99 |
|---|---|---|---|---|---|---|
| **1** (true 0.4 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 471 | 0.19 | 0.24 | 0.47 | 1.03 |
| | system | 471 | 0.07 | 0.10 | 0.20 | 0.58 |
| | US, system sign | 471 | 0.20 | 0.25 | 0.49 | 1.03 |
| | fused, tau 1 mm | 471 | 0.07 | 0.11 | 0.21 | 0.66 |
| | fused, tau 2 mm | 471 | 0.07 | 0.10 | 0.20 | 0.58 |
| | fused, tau 3 mm | 471 | 0.07 | 0.10 | 0.20 | 0.58 |
| **4** (true 1.4 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 470 | 0.78 | 0.99 | 1.99 | 3.91 |
| | system | 470 | 0.19 | 0.31 | 0.65 | 2.03 |
| | US, system sign | 470 | 0.79 | 1.02 | 2.04 | 4.22 |
| | fused, tau 1 mm | 470 | 0.36 | 0.82 | 2.04 | 4.22 |
| | fused, tau 2 mm | 470 | 0.20 | 0.52 | 1.79 | 4.22 |
| | fused, tau 3 mm | 470 | 0.19 | 0.38 | 0.70 | 4.22 |
| **8** (true 2.9 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 459 | 1.83 | 2.24 | 4.22 | 8.17 |
| | system | 459 | 0.24 | 0.41 | 0.90 | 2.99 |
| | US, system sign | 459 | 1.88 | 2.26 | 4.22 | 8.17 |
| | fused, tau 1 mm | 459 | 1.88 | 2.17 | 4.22 | 8.17 |
| | fused, tau 2 mm | 459 | 0.80 | 1.85 | 4.22 | 8.17 |
| | fused, tau 3 mm | 459 | 0.39 | 1.50 | 4.16 | 8.17 |
