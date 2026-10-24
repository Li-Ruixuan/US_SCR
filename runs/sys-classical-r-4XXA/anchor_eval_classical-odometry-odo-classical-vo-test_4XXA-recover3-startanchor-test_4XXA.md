# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 56 | 100 % | 3.0 / 8.0 | 0.38 | 9.8 (2.05) | 3.2 (2.86) | 3.0 (2.37) | 2.8 (2.03) |
| run-402 | 35 | 100 % | 4.0 / 7.4 | 0.38 | 9.5 (0.76) | 4.1 (1.47) | 4.0 (1.19) | 3.6 (0.77) |
| run-403 | 58 | 100 % | 5.0 / 9.3 | 0.47 | 4.1 (0.73) | 5.1 (1.80) | 4.9 (1.47) | 3.6 (0.79) |
| run-404 | 37 | 100 % | 6.7 / 10.7 | 0.68 | 9.1 (0.90) | 6.6 (2.06) | 6.5 (1.66) | 5.9 (0.93) |
| run-405 | 37 | 100 % | 5.6 / 8.0 | 0.42 | 5.6 (1.11) | 4.8 (2.11) | 4.7 (1.61) | 3.7 (1.12) |
| run-406 | 37 | 100 % | 6.8 / 10.8 | 0.46 | 10.7 (0.92) | 6.4 (1.81) | 6.4 (1.47) | 5.7 (0.93) |
| run-407 | 37 | 100 % | 4.2 / 7.6 | 0.47 | 13.4 (1.24) | 4.8 (2.17) | 4.5 (1.70) | 4.2 (1.19) |
| run-408 | 37 | 100 % | 7.0 / 18.5 | 0.55 | 7.3 (1.17) | 7.0 (3.19) | 6.6 (2.64) | 4.5 (1.27) |
| **mean** | | 100 % | 5.3 / 10.0 | 0.48 | 8.7 (1.11) | 5.3 (2.18) | 5.1 (1.77) | 4.2 (1.13) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-test_4XXA --test-root /data2/u0137815/rgbd-us/data/test_4XXA --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-test_4XXA, anchored-causal-classical-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-test_4XXA).
