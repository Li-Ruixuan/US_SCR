# Scene coordinate anchors: scr-v2-4XXA (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (zero). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 210 | 100 % | 4.0 / 6.5 | 0.36 | 59.6 (5.18) | 4.1 (1.97) | 4.1 (1.97) | 8.3 (2.34) |
| run-402 | 133 | 100 % | 6.6 / 7.7 | 0.54 | 30.8 (2.70) | 6.4 (1.31) | 6.4 (1.31) | 7.1 (1.14) |
| run-403 | 217 | 100 % | 5.9 / 7.6 | 0.46 | 34.6 (2.01) | 5.5 (1.34) | 5.5 (1.34) | 6.1 (0.77) |
| run-404 | 140 | 100 % | 9.1 / 12.3 | 0.66 | 29.5 (2.68) | 8.7 (2.79) | 8.7 (2.79) | 9.4 (1.33) |
| run-405 | 140 | 100 % | 6.4 / 9.2 | 0.56 | 35.4 (2.92) | 6.0 (1.82) | 6.0 (1.82) | 7.5 (1.32) |
| run-406 | 140 | 100 % | 3.5 / 6.5 | 0.39 | 26.3 (2.61) | 2.6 (1.50) | 2.6 (1.50) | 4.6 (1.12) |
| run-407 | 140 | 100 % | 4.1 / 7.3 | 0.40 | 28.5 (2.47) | 3.8 (1.85) | 3.8 (1.85) | 5.1 (1.93) |
| run-408 | 140 | 100 % | 4.6 / 10.3 | 0.46 | 23.0 (2.01) | 4.2 (1.87) | 4.2 (1.87) | 6.6 (1.38) |
| **mean** | | 100 % | 5.5 / 8.4 | 0.48 | 33.5 (2.82) | 5.2 (1.81) | 5.2 (1.81) | 6.8 (1.42) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXA-odometry-odo-zero-every0.25s-recover3-startanchor-test_4XXA --test-root /data2/u0137815/rgbd-us/data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v2-4XXA-odometry-odo-zero-every0.25s-recover3-startanchor-test_4XXA, anchored-causal-scr-v2-4XXA-odometry-odo-zero-every0.25s-recover3-startanchor-test_4XXA).
