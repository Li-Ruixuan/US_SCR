# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXE). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-425 | 36 | 94 % | 11.3 / 30.4 | 0.48 | 12.9 (1.87) | 11.5 (4.97) | 10.4 (4.13) | 9.0 (1.99) |
| run-426 | 37 | 97 % | 9.8 / 28.0 | 0.41 | 15.4 (1.73) | 8.8 (5.15) | 8.5 (4.37) | 5.9 (1.85) |
| run-427 | 36 | 64 % | 41.1 / 99.9 | 1.54 | 19.7 (2.14) | 22.9 (6.08) | 19.6 (4.98) | 18.5 (2.40) |
| run-428 | 34 | 82 % | 5.5 / 80.1 | 0.36 | 11.8 (1.26) | 5.9 (3.49) | 5.5 (2.83) | 7.3 (1.66) |
| **mean** | | 84 % | 16.9 / 59.6 | 0.70 | 15.0 (1.75) | 12.2 (4.92) | 11.0 (4.08) | 10.2 (1.98) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE-map-room-401+room-402+room-403+room-404+room-405+room-406 --test-root /data2/u0137815/rgbd-us/data/test_4XXE --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE-map-room-401+room-402+room-403+room-404+room-405+room-406, anchored-causal-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE-map-room-401+room-402+room-403+room-404+room-405+room-406).
