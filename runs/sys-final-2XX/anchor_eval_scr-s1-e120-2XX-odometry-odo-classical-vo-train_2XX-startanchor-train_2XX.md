# Scene coordinate anchors: scr-s1-e120-2XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_2XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-205 | 47 | 100 % | 4.7 / 11.4 | 0.29 | 67.3 (2.87) | 5.4 (4.17) | 5.6 (3.01) | 6.0 (2.80) |
| run-211 | 28 | 100 % | 2.3 / 5.5 | 0.37 | 10.9 (1.63) | 3.7 (2.01) | 3.6 (1.78) | 2.6 (1.65) |
| **mean** | | 100 % | 3.5 / 8.4 | 0.33 | 39.1 (2.25) | 4.6 (3.09) | 4.6 (2.40) | 4.3 (2.22) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-s1-e120-2XX-odometry-odo-classical-vo-train_2XX-startanchor-train_2XX --test-root data/train_2XX --out <folder for this test>` (or anchored-pgo-scr-s1-e120-2XX-odometry-odo-classical-vo-train_2XX-startanchor-train_2XX, anchored-causal-scr-s1-e120-2XX-odometry-odo-classical-vo-train_2XX-startanchor-train_2XX).
