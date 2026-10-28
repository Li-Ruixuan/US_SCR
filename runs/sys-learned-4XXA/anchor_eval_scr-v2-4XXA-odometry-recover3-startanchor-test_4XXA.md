# Scene coordinate anchors: scr-v2-4XXA (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (model). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 56 | 100 % | 3.9 / 5.9 | 0.35 | 71.1 (2.77) | 4.9 (3.87) | 4.0 (1.76) | 7.4 (2.08) |
| run-402 | 35 | 100 % | 6.6 / 7.6 | 0.54 | 52.3 (2.38) | 7.2 (3.30) | 6.3 (1.11) | 6.9 (1.35) |
| run-403 | 58 | 100 % | 5.9 / 7.9 | 0.45 | 25.1 (1.41) | 6.3 (2.14) | 5.5 (0.79) | 5.7 (0.87) |
| run-404 | 37 | 100 % | 9.0 / 12.2 | 0.65 | 43.8 (1.83) | 9.9 (3.25) | 8.5 (1.96) | 9.8 (1.38) |
| run-405 | 37 | 100 % | 6.2 / 9.2 | 0.59 | 45.2 (2.78) | 7.8 (3.90) | 6.0 (1.46) | 9.2 (1.97) |
| run-406 | 37 | 100 % | 3.4 / 6.8 | 0.37 | 16.9 (1.36) | 3.6 (2.09) | 2.7 (1.01) | 4.5 (1.03) |
| run-407 | 37 | 100 % | 4.0 / 7.3 | 0.43 | 49.2 (1.74) | 4.2 (2.66) | 3.9 (1.34) | 4.4 (1.45) |
| run-408 | 37 | 100 % | 4.8 / 8.3 | 0.46 | 21.7 (0.98) | 4.9 (1.84) | 4.4 (1.12) | 4.6 (0.90) |
| **mean** | | 100 % | 5.5 / 8.2 | 0.48 | 40.7 (1.91) | 6.1 (2.88) | 5.2 (1.32) | 6.6 (1.38) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXA-odometry-recover3-startanchor-test_4XXA --test-root /data2/u0137815/rgbd-us/data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v2-4XXA-odometry-recover3-startanchor-test_4XXA, anchored-causal-scr-v2-4XXA-odometry-recover3-startanchor-test_4XXA).
