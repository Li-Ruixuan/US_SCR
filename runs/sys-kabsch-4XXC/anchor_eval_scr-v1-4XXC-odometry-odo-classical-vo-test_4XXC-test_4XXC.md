# Scene coordinate anchors: scr-v1-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXC). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-413 | 37 | 100 % | 3.5 / 5.2 | 0.69 | 7.9 (1.04) | 4.8 (1.36) | 4.8 (1.10) | 4.5 (1.04) |
| run-414 | 37 | 100 % | 5.9 / 11.9 | 0.90 | 9.8 (1.38) | 7.7 (1.94) | 7.8 (1.40) | 8.6 (1.29) |
| run-415 | 37 | 100 % | 5.9 / 11.1 | 0.78 | 6.9 (0.93) | 7.2 (1.52) | 6.9 (1.14) | 6.8 (0.93) |
| run-416 | 37 | 100 % | 5.2 / 11.0 | 0.69 | 11.1 (1.70) | 6.6 (2.38) | 6.4 (1.45) | 5.9 (1.44) |
| **mean** | | 100 % | 5.2 / 9.8 | 0.76 | 8.9 (1.27) | 6.6 (1.80) | 6.5 (1.27) | 6.4 (1.18) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXC-test_4XXC --test-root data/test_4XXC --out <folder for this test>` (or anchored-pgo-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXC-test_4XXC, anchored-causal-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXC-test_4XXC).
