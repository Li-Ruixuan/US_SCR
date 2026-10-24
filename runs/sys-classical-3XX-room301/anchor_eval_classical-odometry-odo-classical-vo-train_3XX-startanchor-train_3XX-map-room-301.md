# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_3XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-315 | 28 | 100 % | 3.5 / 8.3 | 0.48 | 9.4 (1.31) | 3.3 (2.25) | 3.5 (1.73) | 2.9 (1.29) |
| run-316 | 28 | 100 % | 1.8 / 3.5 | 0.21 | 10.9 (1.11) | 1.7 (1.60) | 1.8 (1.21) | 2.2 (1.03) |
| run-317 | 18 | 100 % | 2.7 / 6.5 | 0.28 | 8.5 (1.78) | 3.3 (2.19) | 3.1 (1.86) | 3.7 (1.70) |
| **mean** | | 100 % | 2.7 / 6.1 | 0.32 | 9.6 (1.40) | 2.8 (2.01) | 2.8 (1.60) | 3.0 (1.34) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX-map-room-301 --test-root data/train_3XX --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX-map-room-301, anchored-causal-classical-odometry-odo-classical-vo-train_3XX-startanchor-train_3XX-map-room-301).
