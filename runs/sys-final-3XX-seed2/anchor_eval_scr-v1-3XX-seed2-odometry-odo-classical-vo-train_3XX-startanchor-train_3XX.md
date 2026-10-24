# Scene coordinate anchors: scr-v1-3XX-seed2 (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_3XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 28 | 100 % | 2.3 / 3.0 | 0.17 | 13.0 (0.98) | 2.7 (1.36) | 2.3 (0.82) | 2.7 (0.78) |
| run-314 | 28 | 100 % | 2.5 / 4.6 | 0.19 | 5.3 (0.66) | 2.9 (1.01) | 2.7 (0.71) | 3.0 (0.61) |
| run-315 | 28 | 100 % | 2.3 / 3.6 | 0.18 | 9.3 (1.31) | 2.6 (2.01) | 2.3 (1.43) | 2.0 (1.27) |
| run-316 | 28 | 100 % | 1.6 / 3.3 | 0.13 | 10.5 (1.11) | 1.8 (1.44) | 1.5 (1.07) | 2.2 (1.02) |
| run-317 | 18 | 100 % | 2.1 / 3.2 | 0.25 | 7.1 (1.78) | 2.8 (2.12) | 2.3 (1.80) | 3.8 (1.70) |
| **mean** | | 100 % | 2.2 / 3.5 | 0.19 | 9.0 (1.17) | 2.5 (1.59) | 2.2 (1.17) | 2.7 (1.08) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-3XX-seed2-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX --test-root data/train_3XX --out <folder for this test>` (or anchored-pgo-scr-v1-3XX-seed2-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX, anchored-causal-scr-v1-3XX-seed2-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX).
