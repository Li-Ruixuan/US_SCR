# Scene coordinate anchors: scr-bigclean-2XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_2XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-205 | 47 | 100 % | 4.5 / 9.1 | 0.24 | 68.5 (2.87) | 5.7 (3.56) | 5.0 (2.82) | 6.1 (2.83) |
| run-211 | 28 | 100 % | 3.0 / 5.7 | 0.33 | 11.9 (1.63) | 3.2 (1.82) | 3.0 (1.70) | 2.9 (1.65) |
| **mean** | | 100 % | 3.8 / 7.4 | 0.28 | 40.2 (2.25) | 4.4 (2.69) | 4.0 (2.26) | 4.5 (2.24) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-bigclean-2XX-odometry-odo-classical-vo-train_2XX-recover3-scrframes5-startanchor-train_2XX --test-root /data2/u0137815/rgbd-us/data/train_2XX --out <folder for this test>` (or anchored-pgo-scr-bigclean-2XX-odometry-odo-classical-vo-train_2XX-recover3-scrframes5-startanchor-train_2XX, anchored-causal-scr-bigclean-2XX-odometry-odo-classical-vo-train_2XX-recover3-scrframes5-startanchor-train_2XX).
