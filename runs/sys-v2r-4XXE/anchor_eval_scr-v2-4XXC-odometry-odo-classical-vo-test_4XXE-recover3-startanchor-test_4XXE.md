# Scene coordinate anchors: scr-v2-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXE). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-425 | 37 | 100 % | 6.1 / 9.0 | 0.37 | 13.1 (1.89) | 6.9 (2.42) | 6.8 (2.01) | 5.9 (1.86) |
| run-426 | 37 | 100 % | 6.6 / 11.3 | 0.38 | 15.7 (1.73) | 7.2 (2.39) | 7.3 (1.88) | 6.6 (1.70) |
| run-427 | 27 | 100 % | 6.1 / 9.8 | 0.53 | 16.1 (2.14) | 8.4 (2.87) | 7.6 (1.84) | 10.1 (1.92) |
| run-428 | 35 | 100 % | 2.3 / 7.0 | 0.30 | 12.3 (1.26) | 3.4 (1.77) | 2.9 (1.18) | 3.5 (1.12) |
| **mean** | | 100 % | 5.3 / 9.3 | 0.40 | 14.3 (1.76) | 6.5 (2.36) | 6.1 (1.73) | 6.5 (1.65) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE --test-root /data2/u0137815/rgbd-us/data/test_4XXE --out <folder for this test>` (or anchored-pgo-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE, anchored-causal-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXE-recover3-startanchor-test_4XXE).
