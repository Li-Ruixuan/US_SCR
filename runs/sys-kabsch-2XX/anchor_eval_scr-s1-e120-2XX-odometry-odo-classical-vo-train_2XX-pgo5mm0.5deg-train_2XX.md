# Scene coordinate anchors: scr-s1-e120-2XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (classical-vo-train_2XX). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 5 mm / 0.5 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-205 | 47 | 100 % | 4.7 / 11.4 | 0.29 | 64.1 (2.86) | 5.3 (4.16) | 5.6 (3.00) | 5.7 (2.74) |
| run-211 | 28 | 100 % | 2.3 / 5.5 | 0.37 | 9.7 (1.63) | 3.6 (2.00) | 3.5 (1.78) | 3.1 (1.67) |
| **mean** | | 100 % | 3.5 / 8.4 | 0.33 | 36.9 (2.25) | 4.5 (3.08) | 4.6 (2.39) | 4.4 (2.20) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-s1-e120-2XX-odometry-odo-classical-vo-train_2XX-pgo5mm0.5deg-train_2XX --test-root data/train_2XX --out <folder for this test>` (or anchored-pgo-scr-s1-e120-2XX-odometry-odo-classical-vo-train_2XX-pgo5mm0.5deg-train_2XX, anchored-causal-scr-s1-e120-2XX-odometry-odo-classical-vo-train_2XX-pgo5mm0.5deg-train_2XX).
