# Scene coordinate anchors: scr-v2-3XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (zero). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 105 | 100 % | 1.8 / 2.6 | 0.16 | 27.6 (3.00) | 1.9 (1.24) | 1.9 (1.24) | 2.4 (1.13) |
| run-314 | 105 | 100 % | 1.9 / 4.5 | 0.18 | 53.4 (2.74) | 2.3 (1.68) | 2.3 (1.68) | 3.4 (0.93) |
| run-315 | 105 | 100 % | 2.1 / 3.8 | 0.24 | 31.4 (3.22) | 2.1 (1.88) | 2.1 (1.88) | 6.8 (2.04) |
| run-316 | 105 | 100 % | 1.4 / 2.7 | 0.14 | 66.8 (4.66) | 1.4 (1.62) | 1.4 (1.62) | 4.3 (1.85) |
| run-317 | 70 | 100 % | 2.0 / 2.9 | 0.26 | 65.9 (4.82) | 2.4 (2.00) | 2.4 (2.00) | 7.6 (2.43) |
| **mean** | | 100 % | 1.8 / 3.3 | 0.20 | 49.0 (3.69) | 2.0 (1.69) | 2.0 (1.69) | 4.9 (1.68) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-3XX-odometry-odo-zero-every0.25s-recover3-startanchor-train_3XX --test-root /data2/u0137815/rgbd-us/data/train_3XX --out <folder for this test>` (or anchored-pgo-scr-v2-3XX-odometry-odo-zero-every0.25s-recover3-startanchor-train_3XX, anchored-causal-scr-v2-3XX-odometry-odo-zero-every0.25s-recover3-startanchor-train_3XX).
