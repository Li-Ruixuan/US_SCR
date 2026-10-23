# Scene coordinate anchors: scr-v1-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 100 % | 7.3 / 17.3 | 0.69 | 13.5 (1.09) | 8.4 (1.63) | 8.1 (1.02) | 8.0 (0.94) |
| run-419 | 37 | 100 % | 7.9 / 13.6 | 0.62 | 9.3 (1.54) | 8.6 (2.13) | 8.5 (1.34) | 8.2 (1.34) |
| run-420 | 33 | 100 % | 12.8 / 21.6 | 0.89 | 23.6 (1.27) | 14.5 (2.21) | 14.0 (1.58) | 14.6 (1.20) |
| **mean** | | 100 % | 9.4 / 17.5 | 0.74 | 15.5 (1.30) | 10.5 (1.99) | 10.2 (1.31) | 10.3 (1.16) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-startanchor-test_4XXD --test-root data/test_4XXD --out <folder for this test>` (or anchored-pgo-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-startanchor-test_4XXD, anchored-causal-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-startanchor-test_4XXD).
