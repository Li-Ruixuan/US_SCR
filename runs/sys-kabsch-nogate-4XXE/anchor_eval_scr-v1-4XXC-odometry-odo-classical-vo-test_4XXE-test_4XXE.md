# Scene coordinate anchors: scr-v1-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXE). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-425 | 37 | 100 % | 6.4 / 10.0 | 0.38 | 10.2 (1.89) | 6.7 (2.47) | 6.8 (2.03) | 5.6 (1.86) |
| run-426 | 37 | 100 % | 5.0 / 13.6 | 0.42 | 13.8 (1.73) | 5.7 (2.49) | 4.8 (1.99) | 5.0 (1.72) |
| run-427 | 36 | 94 % | 8.8 / 28.2 | 0.73 | 17.3 (2.14) | 10.0 (4.42) | 9.4 (3.00) | 10.9 (1.85) |
| run-428 | 35 | 100 % | 4.3 / 11.7 | 0.38 | 10.5 (1.26) | 4.4 (1.72) | 4.3 (1.21) | 4.4 (1.14) |
| **mean** | | 99 % | 6.1 / 15.9 | 0.48 | 13.0 (1.76) | 6.7 (2.77) | 6.3 (2.06) | 6.5 (1.64) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXE-test_4XXE --test-root data/test_4XXE --out <folder for this test>` (or anchored-pgo-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXE-test_4XXE, anchored-causal-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXE-test_4XXE).
