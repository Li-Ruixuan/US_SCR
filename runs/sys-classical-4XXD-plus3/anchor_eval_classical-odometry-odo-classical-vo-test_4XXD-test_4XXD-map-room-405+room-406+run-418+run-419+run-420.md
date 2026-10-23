# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at GT. Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-421 | 37 | 100 % | 2.9 / 5.6 | 0.21 | 20.1 (1.97) | 3.8 (2.74) | 2.9 (1.77) | 5.0 (1.68) |
| run-423 | 37 | 97 % | 5.4 / 28.3 | 0.47 | 6.5 (1.33) | 6.6 (3.89) | 6.5 (3.10) | 7.5 (1.34) |
| run-424 | 37 | 100 % | 5.6 / 9.7 | 0.36 | 10.0 (0.71) | 5.7 (1.70) | 5.8 (1.28) | 5.0 (0.63) |
| **mean** | | 99 % | 4.7 / 14.6 | 0.35 | 12.2 (1.34) | 5.3 (2.78) | 5.0 (2.05) | 5.8 (1.22) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXD-test_4XXD-map-room-405+room-406+run-418+run-419+run-420 --test-root data/test_4XXD --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXD-test_4XXD-map-room-405+room-406+run-418+run-419+run-420, anchored-causal-classical-odometry-odo-classical-vo-test_4XXD-test_4XXD-map-room-405+room-406+run-418+run-419+run-420).
