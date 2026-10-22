# Scene coordinate anchors: scr-v1-3XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (zero). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-313 | 105 | 100 % | 1.7 / 2.6 | 0.17 | 25.1 (3.00) | 1.9 (1.33) | 1.9 (1.33) | 2.8 (1.13) |
| run-314 | 105 | 100 % | 2.2 / 4.0 | 0.19 | 52.3 (2.74) | 2.4 (1.59) | 2.4 (1.59) | 3.6 (0.91) |
| run-315 | 105 | 100 % | 2.1 / 3.8 | 0.20 | 31.7 (3.22) | 2.2 (1.94) | 2.2 (1.94) | 5.8 (2.02) |
| run-316 | 105 | 100 % | 1.6 / 3.1 | 0.13 | 70.8 (4.66) | 1.6 (1.50) | 1.6 (1.50) | 4.5 (1.81) |
| run-317 | 70 | 100 % | 2.0 / 2.9 | 0.22 | 64.6 (4.82) | 2.2 (2.08) | 2.2 (2.08) | 6.4 (2.16) |
| **mean** | | 100 % | 1.9 / 3.3 | 0.18 | 48.9 (3.69) | 2.1 (1.69) | 2.1 (1.69) | 4.6 (1.61) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-v1-3XX-odometry-odo-zero-every0.25s-train_3XX --test-root data/train_3XX --out <folder for this test>` (or anchored-pgo-scr-v1-3XX-odometry-odo-zero-every0.25s-train_3XX, anchored-causal-scr-v1-3XX-odometry-odo-zero-every0.25s-train_3XX).
