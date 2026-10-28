# Scene coordinate anchors: scr-v2-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (model). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 140 | 100 % | 6.8 / 13.0 | 0.56 | 42.2 (1.58) | 7.7 (1.47) | 7.7 (1.47) | 7.6 (0.98) |
| run-419 | 140 | 100 % | 7.0 / 13.7 | 0.52 | 32.2 (2.07) | 7.7 (1.68) | 7.7 (1.68) | 8.2 (1.40) |
| run-420 | 126 | 100 % | 11.3 / 17.0 | 0.72 | 50.1 (1.62) | 12.9 (2.11) | 12.9 (2.06) | 13.6 (1.16) |
| run-421 | 119 | 100 % | 7.3 / 11.6 | 0.62 | 19.6 (2.02) | 8.9 (2.65) | 9.1 (2.40) | 9.2 (1.61) |
| run-423 | 140 | 100 % | 10.2 / 13.7 | 0.85 | 27.4 (1.76) | 11.9 (2.53) | 11.9 (2.53) | 11.6 (1.34) |
| run-424 | 140 | 100 % | 7.9 / 9.5 | 0.61 | 46.0 (1.61) | 8.9 (1.16) | 8.9 (1.16) | 9.2 (0.79) |
| **mean** | | 100 % | 8.4 / 13.1 | 0.65 | 36.3 (1.78) | 9.7 (1.93) | 9.7 (1.88) | 9.9 (1.21) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXC-odometry-every0.25s-recover3-startanchor-test_4XXD --test-root /data2/u0137815/rgbd-us/data/test_4XXD --out <folder for this test>` (or anchored-pgo-scr-v2-4XXC-odometry-every0.25s-recover3-startanchor-test_4XXD, anchored-causal-scr-v2-4XXC-odometry-every0.25s-recover3-startanchor-test_4XXD).
