# Scene coordinate anchors: scr-v1-4XXA (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (zero). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-401 | 210 | 100 % | 5.1 / 7.6 | 0.37 | 56.4 (5.18) | 5.2 (2.05) | 5.2 (2.05) | 9.4 (2.36) |
| run-402 | 133 | 100 % | 6.1 / 8.4 | 0.53 | 30.0 (2.70) | 6.0 (1.37) | 6.0 (1.37) | 6.5 (1.16) |
| run-403 | 217 | 100 % | 5.8 / 8.3 | 0.50 | 36.8 (2.01) | 5.5 (1.55) | 5.5 (1.55) | 6.2 (0.78) |
| run-404 | 140 | 100 % | 9.1 / 12.9 | 0.65 | 32.6 (2.68) | 8.8 (2.27) | 8.8 (2.27) | 9.1 (1.32) |
| run-405 | 140 | 100 % | 7.3 / 11.4 | 0.49 | 31.9 (2.92) | 7.2 (2.27) | 7.2 (2.27) | 8.8 (1.39) |
| run-406 | 140 | 100 % | 3.5 / 8.0 | 0.37 | 28.6 (2.61) | 3.2 (1.57) | 3.2 (1.57) | 6.0 (1.11) |
| run-407 | 140 | 100 % | 5.0 / 11.0 | 0.47 | 31.1 (2.47) | 4.9 (1.77) | 4.9 (1.77) | 6.2 (1.94) |
| run-408 | 140 | 100 % | 6.3 / 12.5 | 0.55 | 21.9 (2.01) | 6.3 (1.99) | 6.3 (1.99) | 8.6 (1.46) |
| **mean** | | 100 % | 6.0 / 10.0 | 0.49 | 33.7 (2.82) | 5.9 (1.85) | 5.9 (1.85) | 7.6 (1.44) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-4XXA-odometry-odo-zero-every0.25s-test_4XXA --test-root data/test_4XXA --out <folder for this test>` (or anchored-pgo-scr-v1-4XXA-odometry-odo-zero-every0.25s-test_4XXA, anchored-causal-scr-v1-4XXA-odometry-odo-zero-every0.25s-test_4XXA).
