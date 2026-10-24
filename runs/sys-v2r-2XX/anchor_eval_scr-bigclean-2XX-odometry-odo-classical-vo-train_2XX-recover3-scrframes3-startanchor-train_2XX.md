# Scene coordinate anchors: scr-bigclean-2XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_2XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-205 | 47 | 100 % | 4.1 / 8.7 | 0.24 | 68.5 (2.87) | 5.2 (3.80) | 4.8 (2.80) | 5.8 (2.80) |
| run-211 | 28 | 100 % | 3.1 / 5.3 | 0.34 | 11.9 (1.63) | 3.2 (1.95) | 3.1 (1.74) | 3.0 (1.64) |
| **mean** | | 100 % | 3.6 / 7.0 | 0.29 | 40.2 (2.25) | 4.2 (2.88) | 3.9 (2.27) | 4.4 (2.22) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-bigclean-2XX-odometry-odo-classical-vo-train_2XX-recover3-scrframes3-startanchor-train_2XX --test-root /data2/u0137815/rgbd-us/data/train_2XX --out <folder for this test>` (or anchored-pgo-scr-bigclean-2XX-odometry-odo-classical-vo-train_2XX-recover3-scrframes3-startanchor-train_2XX, anchored-causal-scr-bigclean-2XX-odometry-odo-classical-vo-train_2XX-recover3-scrframes3-startanchor-train_2XX).
