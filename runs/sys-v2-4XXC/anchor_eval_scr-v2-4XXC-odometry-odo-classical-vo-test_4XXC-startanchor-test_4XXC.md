# Scene coordinate anchors: scr-v2-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXC). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-413 | 37 | 100 % | 3.6 / 4.6 | 0.54 | 14.0 (1.04) | 4.3 (1.42) | 4.2 (1.12) | 4.2 (1.04) |
| run-414 | 37 | 100 % | 7.1 / 15.4 | 0.76 | 7.6 (1.38) | 8.2 (1.93) | 8.4 (1.35) | 9.2 (1.28) |
| run-415 | 37 | 100 % | 4.2 / 8.1 | 0.63 | 4.2 (0.93) | 5.3 (1.33) | 5.2 (1.06) | 4.9 (0.93) |
| run-416 | 37 | 100 % | 4.7 / 13.7 | 0.61 | 7.6 (1.71) | 6.1 (2.29) | 5.7 (1.41) | 5.5 (1.46) |
| **mean** | | 100 % | 4.9 / 10.5 | 0.64 | 8.3 (1.27) | 6.0 (1.74) | 5.9 (1.23) | 5.9 (1.17) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXC-startanchor-test_4XXC --test-root data/test_4XXC --out <folder for this test>` (or anchored-pgo-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXC-startanchor-test_4XXC, anchored-causal-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXC-startanchor-test_4XXC).
