# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXC). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-413 | 37 | 100 % | 5.8 / 10.0 | 0.47 | 10.0 (1.05) | 6.1 (2.19) | 5.9 (1.70) | 4.8 (1.08) |
| run-414 | 37 | 100 % | 5.8 / 11.0 | 0.32 | 9.7 (1.38) | 5.5 (2.96) | 5.2 (2.27) | 4.5 (1.30) |
| run-415 | 37 | 100 % | 6.3 / 13.1 | 0.40 | 8.7 (0.93) | 6.2 (3.18) | 5.7 (2.69) | 4.7 (0.97) |
| run-416 | 37 | 100 % | 6.0 / 10.2 | 0.38 | 11.4 (1.70) | 5.8 (3.14) | 5.3 (2.07) | 5.6 (1.41) |
| **mean** | | 100 % | 6.0 / 11.1 | 0.39 | 10.0 (1.27) | 5.9 (2.87) | 5.5 (2.18) | 4.9 (1.19) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-test_4XXC --test-root /data2/u0137815/rgbd-us/data/test_4XXC --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-test_4XXC, anchored-causal-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-test_4XXC).
