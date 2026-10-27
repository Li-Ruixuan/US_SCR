# U3: out-of-plane motion from per-patch speckle decorrelation (test_4XXA)

3389 pairs, patches 12 mm, curve from /data2/u0137815/rgbd-us/data/train_2XX. Out-of-plane error at the 5 US-image points (mm), over pairs. True motion in the header. 'fused': the system unless US differs by more than tau (mean over the points), then US.

| k (rows) | method | pairs | median | mean | p90 | p99 |
|---|---|---|---|---|---|---|
| **1** (true 0.3 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 1145 | 0.17 | 0.24 | 0.51 | 1.15 |
| | system | 1145 | 0.09 | 0.14 | 0.27 | 0.96 |
| | US, system sign | 1145 | 0.20 | 0.27 | 0.53 | 1.19 |
| | fused, tau 1 mm | 1145 | 0.09 | 0.15 | 0.27 | 1.32 |
| | fused, tau 2 mm | 1145 | 0.09 | 0.14 | 0.27 | 0.96 |
| | fused, tau 3 mm | 1145 | 0.09 | 0.14 | 0.27 | 0.96 |
| **4** (true 1.0 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 1147 | 0.54 | 0.76 | 1.76 | 4.02 |
| | system | 1147 | 0.23 | 0.41 | 0.86 | 3.06 |
| | US, system sign | 1147 | 0.57 | 0.82 | 1.82 | 4.11 |
| | fused, tau 1 mm | 1147 | 0.29 | 0.67 | 1.79 | 4.08 |
| | fused, tau 2 mm | 1147 | 0.24 | 0.54 | 1.41 | 4.08 |
| | fused, tau 3 mm | 1147 | 0.24 | 0.48 | 0.98 | 4.08 |
| **8** (true 2.0 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 1097 | 1.08 | 1.64 | 3.90 | 8.78 |
| | system | 1097 | 0.33 | 0.61 | 1.38 | 4.52 |
| | US, system sign | 1097 | 1.16 | 1.70 | 3.98 | 8.78 |
| | fused, tau 1 mm | 1097 | 1.11 | 1.64 | 3.98 | 8.78 |
| | fused, tau 2 mm | 1097 | 0.48 | 1.42 | 3.98 | 8.78 |
| | fused, tau 3 mm | 1097 | 0.40 | 1.22 | 3.91 | 8.78 |
