# Scene coordinate anchors: scr-v1-4XXC (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 100 % | 7.3 / 17.3 | 0.69 | 12.2 (1.09) | 8.4 (1.63) | 8.1 (1.03) | 8.0 (0.94) |
| run-419 | 37 | 100 % | 7.9 / 13.6 | 0.62 | 10.2 (1.55) | 8.6 (2.13) | 8.5 (1.34) | 8.1 (1.35) |
| run-420 | 37 | 92 % | 14.3 / 26.8 | 0.94 | 17.3 (1.27) | 14.5 (2.90) | 12.7 (2.06) | 14.0 (1.20) |
| run-421 | 37 | 100 % | 8.9 / 22.6 | 0.79 | 20.1 (1.97) | 10.4 (3.81) | 10.6 (2.75) | 10.6 (1.83) |
| run-423 | 37 | 100 % | 10.4 / 22.5 | 0.84 | 6.5 (1.33) | 12.1 (2.73) | 11.7 (2.13) | 11.5 (1.37) |
| run-424 | 37 | 100 % | 7.7 / 9.3 | 0.67 | 10.0 (0.71) | 8.8 (1.05) | 8.9 (0.68) | 8.5 (0.59) |
| **mean** | | 99 % | 9.4 / 18.7 | 0.76 | 12.7 (1.32) | 10.5 (2.37) | 10.1 (1.67) | 10.1 (1.21) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-test_4XXD --test-root data/test_4XXD --out <folder for this test>` (or anchored-pgo-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-test_4XXD, anchored-causal-scr-v1-4XXC-odometry-odo-classical-vo-test_4XXD-test_4XXD).
