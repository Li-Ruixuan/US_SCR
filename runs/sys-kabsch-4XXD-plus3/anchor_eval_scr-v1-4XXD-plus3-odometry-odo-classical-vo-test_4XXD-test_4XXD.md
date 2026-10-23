# Scene coordinate anchors: scr-v1-4XXD-plus3 (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-421 | 37 | 100 % | 2.0 / 9.5 | 0.19 | 20.1 (1.97) | 3.1 (2.83) | 2.1 (1.73) | 4.6 (1.70) |
| run-423 | 37 | 100 % | 4.7 / 8.9 | 0.43 | 6.5 (1.33) | 5.7 (2.13) | 5.5 (1.47) | 5.3 (1.23) |
| run-424 | 37 | 100 % | 3.3 / 4.7 | 0.18 | 10.0 (0.71) | 3.5 (0.98) | 3.5 (0.65) | 3.6 (0.60) |
| **mean** | | 100 % | 3.3 / 7.7 | 0.27 | 12.2 (1.34) | 4.1 (1.98) | 3.7 (1.28) | 4.5 (1.18) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXD-plus3-odometry-odo-classical-vo-test_4XXD-test_4XXD --test-root data/test_4XXD --out <folder for this test>` (or anchored-pgo-scr-v1-4XXD-plus3-odometry-odo-classical-vo-test_4XXD-test_4XXD, anchored-causal-scr-v1-4XXD-plus3-odometry-odo-classical-vo-test_4XXD-test_4XXD).
