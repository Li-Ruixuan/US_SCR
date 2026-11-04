# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXC). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-413 | 37 | 100 % | 6.5 / 11.2 | 0.45 | 12.4 (1.05) | 7.2 (2.04) | 6.8 (1.60) | 6.2 (1.08) |
| run-414 | 37 | 100 % | 6.2 / 12.6 | 0.33 | 7.1 (1.38) | 5.9 (2.99) | 5.6 (2.27) | 4.0 (1.30) |
| run-415 | 37 | 100 % | 5.6 / 18.0 | 0.49 | 5.9 (0.93) | 5.9 (3.13) | 6.0 (2.68) | 5.0 (0.99) |
| run-416 | 37 | 100 % | 6.0 / 13.2 | 0.51 | 8.7 (1.70) | 6.6 (3.11) | 6.2 (2.06) | 4.8 (1.44) |
| **mean** | | 100 % | 6.1 / 13.8 | 0.44 | 8.5 (1.27) | 6.4 (2.81) | 6.1 (2.15) | 5.0 (1.20) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-trackerfree-map-4XXC-test_4XXC --test-root /data2/u0137815/rgbd-us/data/test_4XXC --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-trackerfree-map-4XXC-test_4XXC, anchored-causal-classical-odometry-odo-classical-vo-test_4XXC-recover3-startanchor-trackerfree-map-4XXC-test_4XXC).
