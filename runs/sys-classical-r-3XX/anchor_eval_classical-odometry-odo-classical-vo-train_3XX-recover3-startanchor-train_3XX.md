# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_3XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 28 | 100 % | 3.1 / 6.1 | 0.52 | 10.8 (0.97) | 3.6 (1.64) | 3.7 (1.18) | 3.7 (0.80) |
| run-314 | 28 | 100 % | 2.7 / 8.5 | 0.31 | 5.3 (0.66) | 3.4 (1.76) | 3.1 (1.42) | 3.1 (0.64) |
| run-315 | 28 | 100 % | 2.5 / 7.7 | 0.37 | 11.5 (1.31) | 3.0 (2.25) | 2.7 (1.73) | 2.8 (1.30) |
| run-316 | 28 | 100 % | 1.9 / 4.2 | 0.21 | 9.6 (1.11) | 2.2 (1.74) | 1.9 (1.29) | 2.2 (1.03) |
| run-317 | 18 | 100 % | 3.0 / 8.0 | 0.28 | 7.4 (1.78) | 3.6 (2.30) | 3.3 (1.98) | 3.8 (1.71) |
| **mean** | | 100 % | 2.6 / 6.9 | 0.34 | 8.9 (1.17) | 3.2 (1.94) | 2.9 (1.52) | 3.1 (1.09) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-train_3XX --test-root /data2/u0137815/rgbd-us/data/train_3XX --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-train_3XX, anchored-causal-classical-odometry-odo-classical-vo-train_3XX-recover3-startanchor-train_3XX).
