# Classical anchors (SIFT + PnP-RANSAC with depth) (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXD). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-418 | 37 | 100 % | 5.5 / 7.9 | 0.35 | 11.8 (1.08) | 5.2 (1.85) | 5.0 (1.22) | 4.2 (0.92) |
| run-419 | 37 | 100 % | 6.4 / 8.8 | 0.35 | 10.5 (1.54) | 6.2 (2.81) | 6.5 (1.85) | 5.7 (1.28) |
| run-420 | 37 | 92 % | 8.5 / 29.8 | 0.40 | 18.6 (1.27) | 8.1 (3.69) | 7.0 (2.83) | 6.5 (1.18) |
| run-421 | 37 | 100 % | 6.0 / 10.2 | 0.33 | 17.0 (1.96) | 6.3 (3.22) | 5.7 (2.06) | 5.7 (1.70) |
| run-423 | 37 | 97 % | 8.9 / 32.2 | 0.63 | 18.2 (1.30) | 10.6 (4.88) | 10.6 (4.14) | 9.1 (1.40) |
| run-424 | 37 | 100 % | 7.5 / 10.4 | 0.43 | 8.1 (0.70) | 7.4 (1.93) | 7.6 (1.51) | 6.7 (0.66) |
| **mean** | | 98 % | 7.1 / 16.6 | 0.41 | 14.1 (1.31) | 7.3 (3.06) | 7.0 (2.27) | 6.3 (1.19) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD --test-root /data2/u0137815/rgbd-us/data/test_4XXD --out <folder for this test>` (or anchored-pgo-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD, anchored-causal-classical-odometry-odo-classical-vo-test_4XXD-recover3-startanchor-test_4XXD).
