# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 100 % | 6.1 / 10.8 | 0.52 | 13.7 (1.08) | 6.1 (1.89) | 6.0 (1.26) | 5.8 (0.91) |
| run-419 | 37 | 100 % | 8.3 / 12.2 | 0.60 | 12.4 (1.54) | 8.7 (2.77) | 8.5 (1.80) | 7.2 (1.27) |
| run-420 | 37 | 95 % | 9.4 / 28.2 | 0.63 | 22.0 (1.26) | 9.3 (4.31) | 8.5 (3.46) | 7.5 (1.22) |
| run-421 | 37 | 100 % | 7.1 / 11.8 | 0.48 | 18.2 (1.96) | 8.5 (3.16) | 7.6 (2.02) | 6.1 (1.70) |
| run-423 | 37 | 97 % | 12.7 / 33.6 | 0.87 | 22.1 (1.31) | 13.4 (5.33) | 12.6 (4.50) | 10.2 (1.40) |
| run-424 | 37 | 100 % | 8.6 / 11.8 | 0.61 | 6.3 (0.70) | 9.0 (1.95) | 8.2 (1.55) | 7.8 (0.66) |
| **mean** | | 99 % | 8.7 / 18.1 | 0.62 | 15.8 (1.31) | 9.2 (3.23) | 8.6 (2.43) | 7.4 (1.19) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-trackerfree-map-4XXC-test_4XXD --test-root /data2/u0137815/rgbd-us/data/test_4XXD --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-trackerfree-map-4XXC-test_4XXD, anchored-causal-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-trackerfree-map-4XXC-test_4XXD).
