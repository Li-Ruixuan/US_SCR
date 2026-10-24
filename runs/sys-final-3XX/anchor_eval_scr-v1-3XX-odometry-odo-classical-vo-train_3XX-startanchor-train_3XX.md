# Scene coordinate anchors: scr-v1-3XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_3XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 28 | 100 % | 1.8 / 2.7 | 0.20 | 12.3 (0.99) | 2.1 (1.37) | 1.8 (0.82) | 2.0 (0.79) |
| run-314 | 28 | 100 % | 2.3 / 3.6 | 0.19 | 6.5 (0.66) | 2.8 (0.99) | 2.7 (0.69) | 2.9 (0.61) |
| run-315 | 28 | 100 % | 2.1 / 3.9 | 0.20 | 10.3 (1.31) | 2.7 (2.05) | 2.3 (1.44) | 1.9 (1.27) |
| run-316 | 28 | 100 % | 1.6 / 2.8 | 0.13 | 9.5 (1.11) | 1.8 (1.43) | 1.5 (1.08) | 2.0 (1.02) |
| run-317 | 18 | 100 % | 2.1 / 2.7 | 0.21 | 6.2 (1.78) | 2.7 (2.01) | 2.4 (1.72) | 4.0 (1.71) |
| **mean** | | 100 % | 2.0 / 3.1 | 0.19 | 8.9 (1.17) | 2.4 (1.57) | 2.2 (1.15) | 2.6 (1.08) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-3XX-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX --test-root data/train_3XX --out <folder for this test>` (or anchored-pgo-scr-v1-3XX-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX, anchored-causal-scr-v1-3XX-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX).
