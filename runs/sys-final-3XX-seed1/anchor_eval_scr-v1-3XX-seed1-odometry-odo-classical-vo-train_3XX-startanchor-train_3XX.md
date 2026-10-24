# Scene coordinate anchors: scr-v1-3XX-seed1 (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_3XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 28 | 100 % | 1.7 / 2.5 | 0.14 | 12.6 (0.98) | 2.2 (1.34) | 1.8 (0.79) | 2.1 (0.79) |
| run-314 | 28 | 100 % | 2.6 / 4.4 | 0.18 | 4.1 (0.66) | 2.8 (0.97) | 2.8 (0.70) | 3.0 (0.61) |
| run-315 | 28 | 100 % | 2.2 / 3.7 | 0.24 | 10.3 (1.31) | 2.8 (2.09) | 2.4 (1.46) | 2.0 (1.27) |
| run-316 | 28 | 100 % | 1.6 / 3.5 | 0.14 | 10.3 (1.11) | 2.0 (1.48) | 1.6 (1.10) | 2.2 (1.02) |
| run-317 | 18 | 100 % | 2.2 / 3.0 | 0.24 | 6.5 (1.78) | 2.8 (2.02) | 2.4 (1.72) | 4.0 (1.70) |
| **mean** | | 100 % | 2.1 / 3.4 | 0.19 | 8.8 (1.17) | 2.5 (1.58) | 2.2 (1.15) | 2.7 (1.08) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-3XX-seed1-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX --test-root data/train_3XX --out <folder for this test>` (or anchored-pgo-scr-v1-3XX-seed1-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX, anchored-causal-scr-v1-3XX-seed1-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX).
