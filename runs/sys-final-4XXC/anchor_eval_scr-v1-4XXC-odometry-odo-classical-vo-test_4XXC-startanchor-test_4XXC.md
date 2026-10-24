# Scene coordinate anchors: scr-v1-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXC). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-413 | 37 | 100 % | 3.5 / 5.2 | 0.69 | 12.7 (1.04) | 4.9 (1.40) | 4.8 (1.10) | 4.5 (1.04) |
| run-414 | 37 | 100 % | 5.9 / 11.9 | 0.90 | 7.2 (1.38) | 7.7 (1.93) | 7.8 (1.40) | 8.6 (1.29) |
| run-415 | 37 | 100 % | 5.9 / 11.1 | 0.78 | 4.6 (0.93) | 7.3 (1.47) | 7.1 (1.13) | 7.0 (0.94) |
| run-416 | 37 | 100 % | 5.2 / 11.0 | 0.69 | 7.7 (1.71) | 6.6 (2.32) | 6.5 (1.41) | 6.5 (1.43) |
| **mean** | | 100 % | 5.2 / 9.8 | 0.76 | 8.0 (1.27) | 6.6 (1.78) | 6.6 (1.26) | 6.7 (1.17) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXC-startanchor-test_4XXC --test-root data/test_4XXC --out <folder for this test>` (or anchored-pgo-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXC-startanchor-test_4XXC, anchored-causal-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXC-startanchor-test_4XXC).
