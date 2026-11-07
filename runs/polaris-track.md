# Polaris ground truth: volume 950-2400 mm along the tracker axis


## Tracking error against the Polaris distance

### track-v2map-3XX (train_3XX, smoothed 1 s)

All frames: **2.36** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **1.97** mm (4/5 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| 850-900 | 85 | 4 | 3.51 | 3.96 |
| 900-950 | 1654 | 81 | 2.32 | 3.99 |
| 950-1100 | 315 | 15 | 2.43 | 5.61 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 684 | 0.086 | 2.45 |
| middle third | 686 | 0.112 | 2.04 |
| highest third | 684 | 0.152 | 2.57 |

Spearman correlation of error and distance over all frames: -0.09 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

### track-v2map-4XXA (test_4XXA, smoothed 1 s)

All frames: **5.02** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **4.36** mm (3/8 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| < 850 | 1288 | 25 | 4.26 | 7.97 |
| 850-900 | 2038 | 39 | 5.07 | 7.59 |
| 900-950 | 1334 | 26 | 5.21 | 9.27 |
| 950-1100 | 503 | 10 | 4.12 | 8.21 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 1719 | 0.095 | 5.08 |
| middle third | 1725 | 0.128 | 4.24 |
| highest third | 1719 | 0.178 | 4.96 |

Spearman correlation of error and distance over all frames: +0.16 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

### track-v2map-5XXA-exam (test_5XXA, smoothed 1 s)

All frames: **2.28** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **2.58** mm (2/8 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| < 850 | 1437 | 20 | 2.35 | 4.16 |
| 850-900 | 2219 | 31 | 1.84 | 5.28 |
| 900-950 | 3387 | 47 | 2.47 | 5.07 |
| 950-1100 | 102 | 1 | 2.60 | 5.21 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 2379 | 0.080 | 2.13 |
| middle third | 2387 | 0.100 | 2.26 |
| highest third | 2379 | 0.124 | 2.54 |

Spearman correlation of error and distance over all frames: +0.11 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

### track-v2map-5XXA-after (test_5XXA, smoothed 1 s)

All frames: **2.50** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **3.30** mm (2/8 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| < 850 | 1437 | 20 | 1.91 | 6.26 |
| 850-900 | 2219 | 31 | 2.02 | 6.15 |
| 900-950 | 3387 | 47 | 3.03 | 5.38 |
| 950-1100 | 102 | 1 | 2.92 | 9.29 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 2379 | 0.080 | 1.95 |
| middle third | 2387 | 0.100 | 2.30 |
| highest third | 2379 | 0.124 | 3.09 |

Spearman correlation of error and distance over all frames: +0.21 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

### track-v2map-5XXB-generic (test_5XXB, smoothed 1 s)

All frames: **3.36** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **3.25** mm (4/8 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| < 850 | 386 | 5 | 4.91 | 6.50 |
| 850-900 | 2107 | 30 | 3.71 | 9.38 |
| 900-950 | 4070 | 57 | 2.92 | 5.84 |
| 950-1100 | 540 | 8 | 3.45 | 6.03 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 2365 | 0.083 | 3.59 |
| middle third | 2373 | 0.104 | 3.21 |
| highest third | 2365 | 0.136 | 3.18 |

Spearman correlation of error and distance over all frames: -0.23 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

### track-v2map-5XXC-exam (test_5XXC, smoothed 1 s)

All frames: **3.11** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **4.58** mm (5/8 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| < 850 | 626 | 9 | 3.00 | 5.87 |
| 850-900 | 2350 | 33 | 2.60 | 6.34 |
| 900-950 | 3661 | 52 | 2.84 | 5.05 |
| 950-1100 | 457 | 6 | 3.32 | 6.55 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 2362 | 0.077 | 2.86 |
| middle third | 2370 | 0.095 | 2.81 |
| highest third | 2362 | 0.118 | 2.97 |

Spearman correlation of error and distance over all frames: +0.11 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

### track-v2map-5XXD-exam (test_5XXD, smoothed 1 s)

All frames: **2.24** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **nan** mm (0/4 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| < 850 | 463 | 13 | 2.51 | 4.44 |
| 850-900 | 1464 | 41 | 1.97 | 3.56 |
| 900-950 | 1632 | 46 | 2.36 | 3.80 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 1185 | 0.088 | 1.96 |
| middle third | 1189 | 0.109 | 2.21 |
| highest third | 1185 | 0.139 | 2.43 |

Spearman correlation of error and distance over all frames: +0.06 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

### track-v2map-5XXE-exam (test_5XXE, smoothed 1 s)

All frames: **5.85** mm (mean over sweeps of the median; scr_track.md shows the same). Frames inside 950-2400 mm only: **10.73** mm (2/4 sweeps with >= 30 such frames).

| distance band mm | frames | % | error median mm | p90 |
|---|---|---|---|---|
| < 850 | 253 | 8 | 8.04 | 9.94 |
| 850-900 | 1267 | 38 | 4.62 | 7.85 |
| 900-950 | 1678 | 50 | 6.60 | 9.28 |
| 950-1100 | 145 | 4 | 10.85 | 15.46 |

| local tracker noise at the US image (1 s) | frames | noise mm | error median mm |
|---|---|---|---|
| lowest third | 1113 | 0.078 | 5.80 |
| middle third | 1117 | 0.094 | 5.89 |
| highest third | 1113 | 0.117 | 6.47 |

Spearman correlation of error and distance over all frames: +0.30 (distance also changes the view, so the coverage: compare with the coverage of the same frames before blaming Polaris).

## Warnings

- none
