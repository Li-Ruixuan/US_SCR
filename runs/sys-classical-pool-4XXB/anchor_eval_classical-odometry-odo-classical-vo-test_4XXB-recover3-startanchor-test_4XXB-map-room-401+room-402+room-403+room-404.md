# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXB). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-409 | 39 | 97 % | 3.1 / 7.5 | 0.27 | 11.4 (1.40) | 2.6 (2.11) | 2.5 (1.72) | 2.1 (1.37) |
| run-410 | 37 | 100 % | 5.2 / 9.6 | 0.41 | 10.9 (1.38) | 6.0 (2.58) | 5.0 (1.95) | 4.4 (1.29) |
| run-411 | 37 | 100 % | 8.6 / 12.2 | 0.61 | 19.9 (1.31) | 8.8 (3.05) | 8.4 (2.30) | 6.9 (1.30) |
| run-412 | 37 | 100 % | 9.6 / 17.2 | 0.40 | 12.9 (1.57) | 10.3 (3.62) | 9.9 (2.89) | 8.4 (1.51) |
| **mean** | | 99 % | 6.6 / 11.6 | 0.42 | 13.8 (1.41) | 6.9 (2.84) | 6.4 (2.21) | 5.5 (1.37) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB-map-room-401+room-402+room-403+room-404 --test-root /data2/u0137815/rgbd-us/data/test_4XXB --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB-map-room-401+room-402+room-403+room-404, anchored-causal-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB-map-room-401+room-402+room-403+room-404).
