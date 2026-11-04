# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXB). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-409 | 39 | 100 % | 4.3 / 6.5 | 0.44 | 12.9 (1.40) | 4.1 (1.96) | 3.9 (1.59) | 3.5 (1.36) |
| run-410 | 37 | 100 % | 5.3 / 6.1 | 0.56 | 11.3 (1.38) | 4.8 (1.85) | 4.6 (1.30) | 4.5 (1.25) |
| run-411 | 37 | 100 % | 4.1 / 6.9 | 0.48 | 9.5 (1.31) | 4.1 (1.77) | 3.6 (1.37) | 3.9 (1.27) |
| run-412 | 37 | 100 % | 5.3 / 6.8 | 0.53 | 14.1 (1.57) | 5.0 (2.10) | 5.1 (1.46) | 5.3 (1.43) |
| **mean** | | 100 % | 4.7 / 6.6 | 0.50 | 11.9 (1.41) | 4.5 (1.92) | 4.3 (1.43) | 4.3 (1.33) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-trackerfree-map-4XXB-test_4XXB --test-root /data2/u0137815/rgbd-us/data/test_4XXB --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-trackerfree-map-4XXB-test_4XXB, anchored-causal-classical-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-trackerfree-map-4XXB-test_4XXB).
