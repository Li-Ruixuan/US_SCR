# Scene coordinate anchors: scr-v2-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (model). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 100 % | 6.6 / 13.2 | 0.57 | 42.2 (1.58) | 7.7 (2.47) | 7.6 (1.03) | 7.7 (1.11) |
| run-419 | 37 | 100 % | 7.0 / 13.5 | 0.50 | 32.2 (2.07) | 8.0 (3.07) | 7.7 (1.37) | 9.0 (1.58) |
| run-420 | 33 | 100 % | 11.6 / 16.9 | 0.72 | 50.1 (1.62) | 14.5 (2.71) | 12.6 (1.25) | 13.6 (1.19) |
| run-421 | 31 | 100 % | 6.9 / 10.4 | 0.63 | 19.6 (2.02) | 9.2 (3.13) | 8.6 (1.77) | 9.3 (1.81) |
| run-423 | 37 | 100 % | 9.9 / 13.6 | 0.87 | 27.4 (1.76) | 12.1 (2.73) | 11.7 (1.53) | 11.6 (1.45) |
| run-424 | 37 | 100 % | 8.0 / 8.9 | 0.62 | 46.0 (1.61) | 9.5 (2.39) | 8.9 (0.81) | 9.6 (0.91) |
| **mean** | | 100 % | 8.3 / 12.8 | 0.65 | 36.3 (1.78) | 10.2 (2.75) | 9.5 (1.29) | 10.1 (1.34) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXC-odometry-recover3-startanchor-test_4XXD --test-root /data2/u0137815/rgbd-us/data/test_4XXD --out <folder for this test>` (or anchored-pgo-scr-v2-4XXC-odometry-recover3-startanchor-test_4XXD, anchored-causal-scr-v2-4XXC-odometry-recover3-startanchor-test_4XXD).
