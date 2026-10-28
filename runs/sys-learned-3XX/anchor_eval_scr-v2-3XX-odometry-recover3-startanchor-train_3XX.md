# Scene coordinate anchors: scr-v2-3XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (model). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 28 | 100 % | 1.6 / 2.8 | 0.16 | 26.8 (1.81) | 2.6 (2.86) | 1.8 (1.11) | 4.1 (1.48) |
| run-314 | 28 | 100 % | 2.2 / 4.1 | 0.18 | 28.6 (1.38) | 3.2 (2.09) | 2.8 (0.92) | 4.1 (1.01) |
| run-315 | 28 | 100 % | 2.3 / 3.8 | 0.24 | 59.3 (2.36) | 4.0 (3.51) | 2.2 (1.45) | 5.6 (1.79) |
| run-316 | 28 | 100 % | 1.4 / 2.7 | 0.13 | 36.3 (2.44) | 2.8 (3.43) | 1.5 (1.32) | 4.2 (1.83) |
| run-317 | 18 | 100 % | 2.2 / 2.9 | 0.25 | 34.0 (3.30) | 3.9 (4.89) | 3.0 (2.01) | 7.1 (2.70) |
| **mean** | | 100 % | 1.9 / 3.3 | 0.19 | 37.0 (2.26) | 3.3 (3.36) | 2.3 (1.36) | 5.0 (1.76) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-3XX-odometry-recover3-startanchor-train_3XX --test-root /data2/u0137815/rgbd-us/data/train_3XX --out <folder for this test>` (or anchored-pgo-scr-v2-3XX-odometry-recover3-startanchor-train_3XX, anchored-causal-scr-v2-3XX-odometry-recover3-startanchor-train_3XX).
