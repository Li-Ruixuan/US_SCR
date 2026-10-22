# Scene coordinate anchors: scr-v1-4XXA (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 56 | 100 % | 5.3 / 7.2 | 0.38 | 29.2 (2.05) | 5.5 (2.59) | 5.2 (2.10) | 4.8 (2.03) |
| run-402 | 35 | 100 % | 5.8 / 8.2 | 0.54 | 23.0 (0.75) | 5.7 (1.26) | 5.5 (0.96) | 5.8 (0.80) |
| run-403 | 58 | 100 % | 5.8 / 8.4 | 0.48 | 11.4 (0.73) | 5.8 (1.19) | 5.6 (0.93) | 5.3 (0.74) |
| run-404 | 37 | 100 % | 8.9 / 12.7 | 0.67 | 10.6 (0.90) | 8.7 (1.64) | 8.7 (1.23) | 7.9 (0.93) |
| run-405 | 37 | 100 % | 7.3 / 11.7 | 0.51 | 7.6 (1.12) | 7.1 (2.05) | 7.0 (1.48) | 6.5 (1.09) |
| run-406 | 37 | 100 % | 3.0 / 8.5 | 0.38 | 16.2 (0.92) | 4.0 (1.43) | 3.1 (1.06) | 3.4 (0.91) |
| run-407 | 37 | 100 % | 5.1 / 11.6 | 0.46 | 14.1 (1.24) | 5.2 (1.75) | 5.2 (1.44) | 5.2 (1.22) |
| run-408 | 37 | 100 % | 7.0 / 11.1 | 0.54 | 9.5 (1.17) | 6.6 (1.91) | 6.4 (1.44) | 4.9 (1.19) |
| **mean** | | 100 % | 6.0 / 9.9 | 0.49 | 15.2 (1.11) | 6.1 (1.73) | 5.8 (1.33) | 5.5 (1.11) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-test_4XXA --test-root data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-test_4XXA, anchored-causal-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-test_4XXA).
