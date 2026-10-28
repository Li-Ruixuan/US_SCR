# Scene coordinate anchors: scr-bigclean-2XX (odometry retrieval)

Odometry: rpr-rgb-gap8-12XX-gru8 (zero). Anchor every 0.25 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-201 | 364 | 100 % | 2.4 / 4.1 | 0.18 | 44.8 (3.32) | 2.6 (2.22) | 2.6 (2.22) | 3.6 (1.61) |
| run-202 | 175 | 100 % | 2.6 / 4.9 | 0.21 | 38.0 (3.71) | 2.5 (2.57) | 2.5 (2.57) | 4.6 (2.01) |
| run-203 | 175 | 100 % | 2.5 / 4.3 | 0.19 | 36.4 (4.03) | 2.4 (2.77) | 2.4 (2.77) | 4.4 (2.17) |
| run-204 | 175 | 100 % | 4.1 / 8.6 | 0.22 | 24.3 (4.17) | 4.3 (2.76) | 4.3 (2.76) | 10.9 (2.93) |
| run-205 | 175 | 100 % | 4.0 / 8.1 | 0.25 | 29.5 (3.83) | 4.1 (3.37) | 4.1 (3.37) | 9.7 (2.82) |
| run-206 | 175 | 100 % | 3.5 / 6.5 | 0.27 | 43.4 (4.42) | 3.9 (2.57) | 3.9 (2.57) | 7.2 (2.20) |
| run-207 | 171 | 100 % | 4.9 / 7.2 | 0.39 | 32.7 (4.50) | 4.7 (2.99) | 4.7 (3.03) | 8.7 (2.55) |
| run-208 | 175 | 100 % | 3.7 / 6.9 | 0.32 | 30.8 (2.02) | 3.6 (2.82) | 3.6 (2.82) | 4.1 (1.17) |
| run-209 | 175 | 100 % | 3.5 / 6.3 | 0.32 | 26.2 (2.23) | 3.5 (2.44) | 3.5 (2.44) | 5.1 (1.35) |
| run-210 | 105 | 100 % | 4.2 / 5.2 | 0.21 | 20.6 (2.02) | 3.9 (2.07) | 3.9 (2.07) | 4.5 (0.85) |
| run-211 | 105 | 100 % | 3.1 / 5.6 | 0.32 | 31.4 (1.97) | 3.2 (2.26) | 3.2 (2.26) | 3.4 (1.02) |
| run-212 | 84 | 100 % | 3.2 / 4.4 | 0.28 | 63.4 (3.51) | 3.4 (1.68) | 3.4 (1.68) | 6.3 (1.24) |
| **mean** | | 100 % | 3.5 / 6.0 | 0.26 | 35.1 (3.31) | 3.5 (2.54) | 3.5 (2.55) | 6.1 (1.83) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-12XX-gru8/fold*/best.pt --source anchored-offline-scr-bigclean-2XX-odometry-odo-zero-every0.25s-recover3-startanchor-train_2XX --test-root /data2/u0137815/rgbd-us/data/train_2XX --out <folder for this test>` (or anchored-pgo-scr-bigclean-2XX-odometry-odo-zero-every0.25s-recover3-startanchor-train_2XX, anchored-causal-scr-bigclean-2XX-odometry-odo-zero-every0.25s-recover3-startanchor-train_2XX).
