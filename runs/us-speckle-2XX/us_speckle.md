# U3: out-of-plane motion from per-patch speckle decorrelation (train_2XX)

4757 pairs, patches 12 mm, curve built here, leave one sweep out. Out-of-plane error at the 5 US-image points (mm), over pairs. True motion in the header. 'fused': the system unless US differs by more than tau (mean over the points), then US.

| k (rows) | method | pairs | median | mean | p90 | p99 |
|---|---|---|---|---|---|---|
| **1** (true 0.3 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 1595 | 0.22 | 0.29 | 0.61 | 1.22 |
| **4** (true 1.2 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 1587 | 0.62 | 0.86 | 1.99 | 3.76 |
| **8** (true 2.5 mm) | | | | | | |
| | US, Polaris sign (upper bound) | 1575 | 1.31 | 1.91 | 4.41 | 8.20 |

No --system: only the Polaris-sign upper bound is shown.
