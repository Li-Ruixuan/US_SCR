# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-405 | 37 | 100 % | 5.2 / 7.5 | 0.32 | 7.6 (1.12) | 4.9 (1.81) | 4.5 (1.44) | 4.5 (1.09) |
| run-406 | 37 | 100 % | 2.5 / 4.2 | 0.28 | 16.2 (0.92) | 2.8 (1.35) | 2.5 (1.01) | 2.4 (0.89) |
| run-407 | 37 | 100 % | 3.7 / 7.3 | 0.61 | 14.1 (1.24) | 4.5 (2.31) | 3.9 (1.82) | 3.4 (1.24) |
| run-408 | 37 | 100 % | 3.4 / 9.2 | 0.23 | 9.5 (1.17) | 3.1 (2.08) | 3.1 (1.79) | 2.7 (1.19) |
| **mean** | | 100 % | 3.7 / 7.0 | 0.36 | 11.9 (1.11) | 3.8 (1.89) | 3.5 (1.51) | 3.2 (1.10) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXA-test_4XXA-map-room-401+room-402+run-401+run-402+run-403+run-404 --test-root data/test_4XXA --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXA-test_4XXA-map-room-401+room-402+run-401+run-402+run-403+run-404, anchored-causal-classical-odometry-odo-classical-vo-test_4XXA-test_4XXA-map-room-401+room-402+run-401+run-402+run-403+run-404).
