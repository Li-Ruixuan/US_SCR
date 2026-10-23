# Scene coordinate anchors: scr-v1-4XXA-plus4 (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-405 | 37 | 100 % | 2.1 / 5.7 | 0.20 | 7.6 (1.12) | 2.1 (1.62) | 2.2 (1.15) | 2.5 (1.07) |
| run-406 | 37 | 100 % | 1.3 / 2.9 | 0.30 | 16.2 (0.92) | 1.8 (1.35) | 1.6 (1.02) | 1.8 (0.89) |
| run-407 | 37 | 100 % | 2.0 / 4.8 | 0.15 | 14.1 (1.24) | 2.3 (1.61) | 2.2 (1.33) | 2.6 (1.22) |
| run-408 | 37 | 100 % | 2.6 / 5.1 | 0.16 | 9.5 (1.17) | 2.6 (1.54) | 2.5 (1.23) | 2.5 (1.14) |
| **mean** | | 100 % | 2.0 / 4.6 | 0.20 | 11.9 (1.11) | 2.2 (1.53) | 2.1 (1.18) | 2.3 (1.08) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXA-plus4-odometry-odo-classical-vo-test_4XXA-test_4XXA --test-root data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v1-4XXA-plus4-odometry-odo-classical-vo-test_4XXA-test_4XXA, anchored-causal-scr-v1-4XXA-plus4-odometry-odo-classical-vo-test_4XXA-test_4XXA).
