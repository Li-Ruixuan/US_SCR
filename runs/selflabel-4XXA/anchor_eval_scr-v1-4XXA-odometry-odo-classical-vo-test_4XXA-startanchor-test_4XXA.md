# Scene coordinate anchors: scr-v1-4XXA (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 56 | 100 % | 5.3 / 7.2 | 0.38 | 21.6 (2.05) | 5.5 (2.55) | 5.2 (2.08) | 4.7 (2.02) |
| run-402 | 35 | 100 % | 5.8 / 8.2 | 0.54 | 19.5 (0.75) | 5.7 (1.24) | 5.5 (0.95) | 5.7 (0.75) |
| **mean** | | 100 % | 5.5 / 7.7 | 0.46 | 20.5 (1.40) | 5.6 (1.89) | 5.3 (1.52) | 5.2 (1.39) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-startanchor-test_4XXA --test-root data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-startanchor-test_4XXA, anchored-causal-scr-v1-4XXA-odometry-odo-classical-vo-test_4XXA-startanchor-test_4XXA).
