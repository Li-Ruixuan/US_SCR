# U3: out-of-plane motion from per-patch speckle decorrelation (test_4XXD)

2299 pairs, patches 12 mm, curve from /data2/u0137815/rgbd-us/data/train_2XX. Out-of-plane error at the 5 US-image points (mm), over pairs. True motion in the header. 'fused': the system unless US differs by more than tau (mean over the points), then US.

| k (rows) | method | pairs | median | mean | p90 | p99 |
|---|---|---|---|---|---|---|
| **1** (true 0.2 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 762 | 0.16 | 0.20 | 0.36 | 0.77 |
| | system | 762 | 0.08 | 0.12 | 0.25 | 0.65 |
| | US, system sign | 762 | 0.18 | 0.22 | 0.39 | 0.82 |
| | fused, tau 1 mm | 762 | 0.08 | 0.13 | 0.26 | 0.71 |
| | fused, tau 2 mm | 762 | 0.08 | 0.12 | 0.25 | 0.65 |
| | fused, tau 3 mm | 762 | 0.08 | 0.12 | 0.25 | 0.65 |
| **4** (true 1.0 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 783 | 0.52 | 0.64 | 1.29 | 2.50 |
| | system | 783 | 0.23 | 0.36 | 0.82 | 1.95 |
| | US, system sign | 783 | 0.56 | 0.69 | 1.32 | 2.88 |
| | fused, tau 1 mm | 783 | 0.30 | 0.53 | 1.29 | 2.88 |
| | fused, tau 2 mm | 783 | 0.24 | 0.40 | 0.87 | 2.83 |
| | fused, tau 3 mm | 783 | 0.23 | 0.37 | 0.82 | 2.03 |
| **8** (true 2.0 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 754 | 1.06 | 1.39 | 3.00 | 5.75 |
| | system | 754 | 0.34 | 0.54 | 1.22 | 2.95 |
| | US, system sign | 754 | 1.14 | 1.44 | 3.00 | 5.78 |
| | fused, tau 1 mm | 754 | 1.06 | 1.34 | 3.00 | 5.78 |
| | fused, tau 2 mm | 754 | 0.47 | 1.08 | 3.00 | 5.75 |
| | fused, tau 3 mm | 754 | 0.38 | 0.87 | 2.62 | 5.75 |
