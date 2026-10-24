# Scene coordinate anchors: scr-v2-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 100 % | 6.6 / 13.2 | 0.57 | 12.9 (1.09) | 7.8 (1.54) | 7.5 (0.98) | 7.4 (0.93) |
| run-419 | 37 | 100 % | 7.0 / 13.5 | 0.50 | 9.8 (1.55) | 7.9 (2.02) | 7.6 (1.25) | 7.4 (1.33) |
| run-420 | 33 | 100 % | 11.6 / 16.9 | 0.72 | 24.3 (1.27) | 13.2 (1.98) | 12.7 (1.31) | 13.3 (1.13) |
| run-421 | 31 | 100 % | 6.9 / 10.4 | 0.63 | 20.6 (1.96) | 9.0 (2.66) | 8.6 (1.86) | 8.5 (1.83) |
| run-423 | 37 | 100 % | 9.9 / 13.6 | 0.87 | 12.2 (1.32) | 12.1 (2.12) | 11.8 (1.49) | 12.0 (1.27) |
| run-424 | 37 | 100 % | 8.0 / 8.9 | 0.62 | 8.0 (0.70) | 9.1 (0.99) | 8.8 (0.65) | 9.1 (0.60) |
| **mean** | | 100 % | 8.3 / 12.8 | 0.65 | 14.6 (1.32) | 9.8 (1.89) | 9.5 (1.26) | 9.6 (1.18) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD --test-root /data2/u0137815/rgbd-us/data/test_4XXD --out <folder for this test>` (or anchored-pgo-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD, anchored-causal-scr-v2-4XXC-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD).
