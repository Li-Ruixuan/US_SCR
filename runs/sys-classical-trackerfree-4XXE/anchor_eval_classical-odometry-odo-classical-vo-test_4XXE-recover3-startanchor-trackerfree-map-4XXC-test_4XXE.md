# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXE). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-425 | 37 | 100 % | 6.3 / 11.5 | 0.60 | 20.0 (1.87) | 6.3 (3.58) | 6.4 (2.87) | 6.0 (1.86) |
| run-426 | 37 | 100 % | 4.9 / 9.6 | 0.52 | 14.2 (1.72) | 5.7 (3.10) | 4.8 (2.41) | 4.2 (1.66) |
| run-427 | 37 | 100 % | 8.8 / 11.8 | 0.52 | 20.0 (2.15) | 9.2 (3.48) | 8.6 (2.11) | 7.7 (1.69) |
| run-428 | 35 | 100 % | 5.7 / 9.4 | 0.58 | 10.7 (1.25) | 5.9 (2.05) | 5.5 (1.47) | 5.1 (1.12) |
| **mean** | | 100 % | 6.5 / 10.6 | 0.55 | 16.2 (1.75) | 6.8 (3.05) | 6.3 (2.22) | 5.7 (1.58) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-trackerfree-map-4XXC-test_4XXE --test-root /data2/u0137815/rgbd-us/data/test_4XXE --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-trackerfree-map-4XXC-test_4XXE, anchored-causal-classical-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-trackerfree-map-4XXC-test_4XXE).
