# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 56 | 100 % | 5.9 / 9.5 | 0.63 | 13.2 (2.05) | 6.1 (2.80) | 6.1 (2.34) | 5.8 (2.03) |
| run-402 | 35 | 100 % | 6.0 / 9.4 | 0.67 | 9.0 (0.75) | 5.9 (1.43) | 5.6 (1.15) | 5.9 (0.76) |
| run-403 | 58 | 100 % | 6.4 / 10.1 | 0.70 | 8.2 (0.73) | 6.3 (1.66) | 6.2 (1.34) | 5.6 (0.77) |
| run-404 | 37 | 100 % | 8.0 / 12.2 | 0.95 | 12.3 (0.90) | 7.7 (1.91) | 7.6 (1.53) | 6.7 (0.92) |
| run-405 | 37 | 100 % | 5.8 / 8.9 | 0.65 | 5.5 (1.11) | 6.0 (1.94) | 6.1 (1.49) | 5.9 (1.10) |
| run-406 | 37 | 97 % | 7.2 / 10.3 | 0.61 | 10.1 (0.93) | 6.8 (1.73) | 6.2 (1.38) | 4.7 (0.93) |
| run-407 | 37 | 100 % | 6.1 / 9.9 | 0.70 | 10.4 (1.24) | 6.4 (2.11) | 6.0 (1.64) | 5.7 (1.20) |
| run-408 | 37 | 78 % | 10.6 / 62.7 | 0.71 | 7.1 (1.17) | 9.8 (4.33) | 10.7 (3.69) | 11.4 (1.94) |
| **mean** | | 97 % | 7.0 / 16.6 | 0.70 | 9.5 (1.11) | 6.9 (2.24) | 6.8 (1.82) | 6.5 (1.21) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-trackerfree-map-4XXA-test_4XXA --test-root /data2/u0137815/rgbd-us/data/test_4XXA --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-trackerfree-map-4XXA-test_4XXA, anchored-causal-classical-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-trackerfree-map-4XXA-test_4XXA).
