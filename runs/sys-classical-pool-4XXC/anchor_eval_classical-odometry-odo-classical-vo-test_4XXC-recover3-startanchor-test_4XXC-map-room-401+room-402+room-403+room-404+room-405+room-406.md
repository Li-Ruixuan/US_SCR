# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXC). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-413 | 37 | 76 % | 13.7 / 86.6 | 0.70 | 10.0 (1.05) | 8.7 (5.35) | 11.9 (4.77) | 13.4 (1.20) |
| run-414 | 33 | 76 % | 30.7 / 60.1 | 1.02 | 11.6 (1.38) | 18.3 (6.93) | 25.4 (5.97) | 25.6 (1.57) |
| run-415 | 37 | 78 % | 23.5 / 72.5 | 1.15 | 5.2 (0.93) | 20.1 (4.92) | 23.4 (4.29) | 26.0 (1.30) |
| run-416 | 37 | 76 % | 24.0 / 83.1 | 1.01 | 11.4 (1.70) | 18.4 (5.95) | 20.6 (4.60) | 19.2 (1.76) |
| **mean** | | 76 % | 23.0 / 75.6 | 0.97 | 9.6 (1.27) | 16.4 (5.79) | 20.3 (4.91) | 21.1 (1.46) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-test_4XXC-map-room-401+room-402+room-403+room-404+room-405+room-406 --test-root /data2/u0137815/rgbd-us/data/test_4XXC --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-test_4XXC-map-room-401+room-402+room-403+room-404+room-405+room-406, anchored-causal-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-test_4XXC-map-room-401+room-402+room-403+room-404+room-405+room-406).
