# Scene coordinate anchors: scr-v2-4XXA (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXA). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 56 | 100 % | 3.9 / 5.9 | 0.35 | 20.0 (2.04) | 4.3 (2.52) | 4.1 (2.07) | 3.7 (2.02) |
| run-402 | 35 | 100 % | 6.6 / 7.6 | 0.54 | 21.4 (0.75) | 6.2 (1.14) | 6.2 (0.86) | 6.1 (0.75) |
| run-403 | 58 | 100 % | 5.9 / 7.9 | 0.45 | 13.2 (0.73) | 5.6 (1.11) | 5.6 (0.85) | 5.4 (0.73) |
| run-404 | 37 | 95 % | 9.0 / 12.2 | 0.65 | 16.4 (0.90) | 8.9 (2.24) | 8.7 (1.77) | 8.2 (1.01) |
| run-405 | 37 | 100 % | 6.2 / 9.2 | 0.59 | 12.6 (1.11) | 6.1 (1.77) | 5.9 (1.24) | 5.9 (1.06) |
| run-406 | 37 | 100 % | 3.4 / 6.8 | 0.37 | 13.2 (0.92) | 2.9 (1.40) | 2.6 (1.06) | 3.0 (0.90) |
| run-407 | 37 | 100 % | 4.0 / 7.3 | 0.43 | 13.8 (1.23) | 4.0 (1.82) | 4.0 (1.44) | 4.0 (1.20) |
| run-408 | 37 | 100 % | 4.8 / 8.3 | 0.46 | 8.0 (1.17) | 4.3 (1.85) | 4.2 (1.41) | 3.7 (1.16) |
| **mean** | | 99 % | 5.5 / 8.2 | 0.48 | 14.8 (1.11) | 5.3 (1.73) | 5.2 (1.34) | 5.0 (1.10) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXA-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-test_4XXA --test-root /data2/u0137815/rgbd-us/data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v2-4XXA-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-test_4XXA, anchored-causal-scr-v2-4XXA-odometry-odo-classical-vo-test_4XXA-recover3-startanchor-test_4XXA).
