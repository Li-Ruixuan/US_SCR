# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_3XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 28 | 100 % | 5.1 / 7.3 | 0.39 | 9.8 (0.97) | 5.3 (1.61) | 5.2 (1.17) | 5.5 (0.81) |
| run-314 | 28 | 100 % | 3.8 / 9.7 | 0.26 | 3.9 (0.66) | 3.9 (1.85) | 3.7 (1.48) | 3.6 (0.64) |
| run-315 | 28 | 100 % | 3.8 / 7.3 | 0.26 | 11.4 (1.31) | 3.6 (2.40) | 3.3 (1.88) | 2.9 (1.32) |
| run-316 | 28 | 100 % | 2.6 / 4.3 | 0.19 | 9.5 (1.12) | 2.4 (1.77) | 2.2 (1.33) | 2.4 (1.04) |
| run-317 | 18 | 100 % | 4.0 / 7.6 | 0.32 | 9.2 (1.78) | 4.3 (2.42) | 4.3 (2.03) | 4.1 (1.71) |
| **mean** | | 100 % | 3.9 / 7.3 | 0.28 | 8.8 (1.17) | 3.9 (2.01) | 3.8 (1.58) | 3.7 (1.10) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-trackerfree-map-3XX-train_3XX --test-root /data2/u0137815/rgbd-us/data/train_3XX --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-trackerfree-map-3XX-train_3XX, anchored-causal-classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-trackerfree-map-3XX-train_3XX).
