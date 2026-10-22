# Scene coordinate anchors: scr-v1-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 100 % | 7.3 / 17.3 | 0.69 | 12.2 (1.09) | 8.4 (1.63) | 8.1 (1.03) | 8.0 (0.94) |
| run-419 | 37 | 100 % | 7.9 / 13.6 | 0.62 | 10.2 (1.55) | 8.6 (2.13) | 8.5 (1.34) | 8.1 (1.35) |
| run-420 | 33 | 100 % | 12.8 / 21.6 | 0.89 | 17.3 (1.27) | 14.5 (2.27) | 14.0 (1.60) | 14.6 (1.21) |
| run-421 | 31 | 100 % | 8.2 / 15.5 | 0.77 | 20.1 (1.97) | 10.7 (2.88) | 10.6 (2.02) | 10.5 (1.84) |
| run-423 | 36 | 100 % | 9.9 / 22.8 | 0.85 | 6.5 (1.33) | 12.1 (2.50) | 11.7 (1.88) | 11.5 (1.36) |
| run-424 | 37 | 100 % | 7.7 / 9.3 | 0.67 | 10.0 (0.71) | 8.8 (1.05) | 8.9 (0.68) | 8.5 (0.59) |
| **mean** | | 100 % | 9.0 / 16.7 | 0.75 | 12.7 (1.32) | 10.5 (2.08) | 10.3 (1.43) | 10.2 (1.22) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-test_4XXD --test-root data/test_4XXD --out <folder for this test>` (or anchored-pgo-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-test_4XXD, anchored-causal-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-test_4XXD).
