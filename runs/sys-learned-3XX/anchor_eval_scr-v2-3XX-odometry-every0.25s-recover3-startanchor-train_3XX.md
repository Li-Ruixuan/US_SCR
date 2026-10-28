# Scene coordinate anchors: scr-v2-3XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (model). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 105 | 100 % | 1.8 / 2.6 | 0.16 | 26.8 (1.81) | 1.9 (1.24) | 1.9 (1.24) | 2.3 (1.25) |
| run-314 | 105 | 100 % | 1.9 / 4.5 | 0.18 | 28.6 (1.38) | 2.3 (1.68) | 2.3 (1.68) | 3.1 (0.88) |
| run-315 | 105 | 100 % | 2.1 / 3.8 | 0.24 | 59.3 (2.36) | 2.1 (1.88) | 2.1 (1.88) | 3.7 (1.56) |
| run-316 | 105 | 100 % | 1.4 / 2.7 | 0.14 | 36.3 (2.44) | 1.4 (1.62) | 1.4 (1.62) | 2.6 (1.53) |
| run-317 | 70 | 100 % | 2.0 / 2.9 | 0.26 | 34.0 (3.30) | 2.4 (2.00) | 2.4 (2.00) | 4.4 (2.34) |
| **mean** | | 100 % | 1.8 / 3.3 | 0.20 | 37.0 (2.26) | 2.0 (1.69) | 2.0 (1.69) | 3.2 (1.51) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-3XX-odometry-every0.25s-recover3-startanchor-train_3XX --test-root /data2/u0137815/rgbd-us/data/train_3XX --out <folder for this test>` (or anchored-pgo-scr-v2-3XX-odometry-every0.25s-recover3-startanchor-train_3XX, anchored-causal-scr-v2-3XX-odometry-every0.25s-recover3-startanchor-train_3XX).
