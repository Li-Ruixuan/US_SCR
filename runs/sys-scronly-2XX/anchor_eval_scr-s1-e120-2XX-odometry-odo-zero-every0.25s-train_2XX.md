# Scene coordinate anchors: scr-s1-e120-2XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (zero). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-205 | 175 | 100 % | 4.1 / 9.7 | 0.29 | 25.1 (3.83) | 4.3 (3.61) | 4.3 (3.61) | 9.6 (2.84) |
| run-211 | 105 | 100 % | 2.5 / 6.1 | 0.36 | 28.4 (1.97) | 3.3 (2.13) | 3.3 (2.13) | 3.2 (1.04) |
| **mean** | | 100 % | 3.3 / 7.9 | 0.33 | 26.8 (2.90) | 3.8 (2.87) | 3.8 (2.87) | 6.4 (1.94) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-s1-e120-2XX-odometry-odo-zero-every0.25s-train_2XX --test-root data/train_2XX --out <folder for this test>` (or anchored-pgo-scr-s1-e120-2XX-odometry-odo-zero-every0.25s-train_2XX, anchored-causal-scr-s1-e120-2XX-odometry-odo-zero-every0.25s-train_2XX).
