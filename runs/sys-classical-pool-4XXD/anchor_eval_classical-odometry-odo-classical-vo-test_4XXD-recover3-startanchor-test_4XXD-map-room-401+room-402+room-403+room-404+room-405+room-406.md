# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 78 % | 7.3 / 81.6 | 0.45 | 14.0 (1.09) | 7.2 (4.42) | 7.5 (3.71) | 9.5 (1.24) |
| run-419 | 37 | 81 % | 29.8 / 85.5 | 0.98 | 15.0 (1.54) | 31.4 (6.69) | 29.0 (5.59) | 28.9 (1.81) |
| run-420 | 37 | 65 % | 49.5 / 94.5 | 1.73 | 18.6 (1.27) | 51.2 (5.31) | 48.9 (4.46) | 45.0 (2.14) |
| run-421 | 35 | 54 % | 15.6 / 83.2 | 0.91 | 19.0 (1.96) | 22.3 (4.73) | 11.2 (3.87) | 16.8 (2.04) |
| run-423 | 36 | 94 % | 6.2 / 30.6 | 0.34 | 18.2 (1.30) | 7.5 (4.11) | 6.8 (3.47) | 4.7 (1.48) |
| run-424 | 37 | 97 % | 9.5 / 37.8 | 0.45 | 7.6 (0.71) | 10.1 (4.64) | 8.7 (4.21) | 8.3 (1.02) |
| **mean** | | 78 % | 19.6 / 68.9 | 0.81 | 15.4 (1.31) | 21.6 (4.98) | 18.7 (4.22) | 18.9 (1.62) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD-map-room-401+room-402+room-403+room-404+room-405+room-406 --test-root /data2/u0137815/rgbd-us/data/test_4XXD --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD-map-room-401+room-402+room-403+room-404+room-405+room-406, anchored-causal-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD-map-room-401+room-402+room-403+room-404+room-405+room-406).
