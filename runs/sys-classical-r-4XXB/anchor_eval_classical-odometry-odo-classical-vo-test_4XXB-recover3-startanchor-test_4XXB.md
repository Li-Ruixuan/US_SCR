# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXB). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-409 | 39 | 100 % | 3.0 / 5.8 | 0.26 | 13.8 (1.40) | 2.6 (1.93) | 2.5 (1.58) | 2.1 (1.36) |
| run-410 | 37 | 100 % | 3.0 / 3.8 | 0.24 | 12.8 (1.38) | 3.5 (1.80) | 3.2 (1.28) | 3.5 (1.25) |
| run-411 | 37 | 100 % | 2.9 / 5.6 | 0.26 | 11.1 (1.31) | 3.2 (1.78) | 2.9 (1.34) | 3.8 (1.26) |
| run-412 | 37 | 100 % | 3.8 / 4.9 | 0.22 | 14.6 (1.57) | 4.0 (2.11) | 3.9 (1.48) | 4.2 (1.43) |
| **mean** | | 100 % | 3.2 / 5.0 | 0.25 | 13.0 (1.41) | 3.3 (1.90) | 3.1 (1.42) | 3.4 (1.32) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB --test-root /data2/u0137815/rgbd-us/data/test_4XXB --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB, anchored-causal-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB).
