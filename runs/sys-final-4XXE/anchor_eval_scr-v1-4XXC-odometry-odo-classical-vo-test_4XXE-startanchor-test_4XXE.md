# Scene coordinate anchors: scr-v1-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXE). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-425 | 37 | 100 % | 6.4 / 10.0 | 0.38 | 9.8 (1.89) | 6.9 (2.46) | 6.8 (2.02) | 6.4 (1.86) |
| run-426 | 37 | 100 % | 5.0 / 13.6 | 0.42 | 11.9 (1.73) | 5.9 (2.51) | 4.8 (1.99) | 4.8 (1.71) |
| run-427 | 27 | 100 % | 8.1 / 12.6 | 0.69 | 16.0 (2.15) | 9.9 (3.16) | 9.1 (1.84) | 10.5 (1.86) |
| run-428 | 35 | 100 % | 4.3 / 11.7 | 0.38 | 12.6 (1.26) | 4.7 (1.76) | 4.4 (1.23) | 4.5 (1.14) |
| **mean** | | 100 % | 5.9 / 12.0 | 0.47 | 12.6 (1.76) | 6.8 (2.47) | 6.3 (1.77) | 6.6 (1.64) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXE-startanchor-test_4XXE --test-root data/test_4XXE --out <folder for this test>` (or anchored-pgo-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXE-startanchor-test_4XXE, anchored-causal-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXE-startanchor-test_4XXE).
