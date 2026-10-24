# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_2XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-205 | 47 | 100 % | 6.5 / 15.6 | 0.27 | 56.2 (2.88) | 7.1 (4.70) | 6.6 (3.76) | 5.6 (2.89) |
| run-211 | 28 | 100 % | 3.9 / 8.3 | 0.38 | 11.5 (1.63) | 3.7 (2.13) | 3.6 (1.91) | 2.7 (1.64) |
| **mean** | | 100 % | 5.2 / 11.9 | 0.33 | 33.9 (2.26) | 5.4 (3.41) | 5.1 (2.83) | 4.2 (2.27) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-train_2XX-startanchor-train_2XX --test-root data/train_2XX --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-train_2XX-startanchor-train_2XX, anchored-causal-classical-odometry-odo-classical-vo-train_2XX-startanchor-train_2XX).
