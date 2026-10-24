# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXE). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-425 | 37 | 100 % | 5.2 / 9.1 | 0.41 | 17.6 (1.87) | 5.7 (3.39) | 5.4 (2.71) | 5.0 (1.85) |
| run-426 | 37 | 100 % | 5.0 / 9.4 | 0.35 | 13.6 (1.73) | 5.5 (3.09) | 4.6 (2.32) | 3.5 (1.64) |
| run-427 | 37 | 100 % | 6.1 / 8.7 | 0.35 | 19.7 (2.14) | 7.0 (3.50) | 5.9 (2.03) | 7.1 (1.66) |
| run-428 | 35 | 100 % | 4.3 / 6.5 | 0.32 | 13.5 (1.26) | 4.4 (1.98) | 4.3 (1.36) | 4.2 (1.11) |
| **mean** | | 100 % | 5.2 / 8.4 | 0.36 | 16.1 (1.75) | 5.6 (2.99) | 5.1 (2.10) | 5.0 (1.57) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE --test-root /data2/u0137815/rgbd-us/data/test_4XXE --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE, anchored-causal-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE).
