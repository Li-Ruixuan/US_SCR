# Scene coordinate anchors: scr-v1-4XXB (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXB). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-409 | 39 | 100 % | 6.5 / 7.6 | 0.35 | 12.3 (1.40) | 7.1 (1.64) | 7.0 (1.42) | 7.1 (1.37) |
| run-410 | 37 | 100 % | 4.8 / 6.2 | 0.38 | 16.4 (1.38) | 4.8 (1.86) | 4.7 (1.30) | 4.8 (1.27) |
| run-411 | 37 | 100 % | 5.4 / 8.0 | 0.38 | 9.6 (1.30) | 5.4 (2.19) | 5.5 (1.65) | 3.9 (1.24) |
| run-412 | 37 | 100 % | 7.7 / 11.5 | 0.42 | 15.1 (1.57) | 7.9 (2.24) | 7.9 (1.62) | 8.2 (1.47) |
| **mean** | | 100 % | 6.1 / 8.3 | 0.38 | 13.4 (1.41) | 6.3 (1.98) | 6.3 (1.50) | 6.0 (1.34) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXB-odometry-odo-classical-vo-test_4XXB-startanchor-test_4XXB --test-root data/test_4XXB --out <folder for this test>` (or anchored-pgo-scr-v1-4XXB-odometry-odo-classical-vo-test_4XXB-startanchor-test_4XXB, anchored-causal-scr-v1-4XXB-odometry-odo-classical-vo-test_4XXB-startanchor-test_4XXB).
