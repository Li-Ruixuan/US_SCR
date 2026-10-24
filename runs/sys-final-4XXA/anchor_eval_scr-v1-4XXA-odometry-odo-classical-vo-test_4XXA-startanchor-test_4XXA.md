# Scene coordinate anchors: scr-v1-4XXA (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 56 | 100 % | 5.3 / 7.2 | 0.38 | 21.6 (2.05) | 5.5 (2.55) | 5.2 (2.08) | 4.7 (2.02) |
| run-402 | 35 | 100 % | 5.8 / 8.2 | 0.54 | 19.5 (0.75) | 5.7 (1.24) | 5.5 (0.95) | 5.7 (0.75) |
| run-403 | 58 | 100 % | 5.8 / 8.4 | 0.48 | 14.8 (0.73) | 5.8 (1.20) | 5.6 (0.93) | 5.3 (0.73) |
| run-404 | 37 | 100 % | 8.9 / 12.7 | 0.67 | 17.0 (0.90) | 8.9 (1.68) | 8.7 (1.25) | 8.0 (0.92) |
| run-405 | 37 | 100 % | 7.3 / 11.7 | 0.51 | 15.8 (1.11) | 7.2 (2.00) | 7.0 (1.42) | 6.6 (1.08) |
| run-406 | 37 | 100 % | 3.0 / 8.5 | 0.38 | 13.2 (0.92) | 4.0 (1.42) | 3.2 (1.07) | 3.8 (0.91) |
| run-407 | 37 | 100 % | 5.1 / 11.6 | 0.46 | 13.8 (1.23) | 5.2 (1.73) | 5.2 (1.43) | 5.4 (1.21) |
| run-408 | 37 | 100 % | 7.0 / 11.1 | 0.54 | 8.6 (1.17) | 6.6 (1.88) | 6.4 (1.43) | 4.9 (1.18) |
| **mean** | | 100 % | 6.0 / 9.9 | 0.49 | 15.5 (1.11) | 6.1 (1.71) | 5.9 (1.32) | 5.5 (1.10) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-startanchor-test_4XXA --test-root data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-startanchor-test_4XXA, anchored-causal-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-startanchor-test_4XXA).
