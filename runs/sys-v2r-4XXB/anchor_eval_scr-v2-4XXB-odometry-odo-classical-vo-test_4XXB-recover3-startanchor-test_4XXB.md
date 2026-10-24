# Scene coordinate anchors: scr-v2-4XXB (odometry retrieval)

Odometry: rpr-rgb-gap8-123XX-gru8 (classical-vo-test_4XXB). Anchor every 1 s, 3 keyframes averaged, gate 50 mm, reset to the anchor; pose graph: anchor sigma 11 mm / 1 deg, odometry growth 29 mm²/s / 0.1 deg²/s. Segment starts at a pose from the anchor network, no prior (start error per sweep: worst segment). Median error at the US image (mm); in brackets the mean step-to-step error (mm), which matters for a smooth reconstruction.

| Sweep | anchors | accepted | anchor error mm (median / p90) | anchor error deg | unanchored | causal | offline | offline pose graph |
|---|---|---|---|---|---|---|---|---|
| run-409 | 39 | 100 % | 6.2 / 7.4 | 0.34 | 12.2 (1.40) | 6.8 (1.65) | 6.7 (1.40) | 6.7 (1.36) |
| run-410 | 37 | 100 % | 5.8 / 8.3 | 0.40 | 15.9 (1.38) | 5.4 (1.80) | 5.3 (1.26) | 5.6 (1.27) |
| run-411 | 37 | 100 % | 3.9 / 6.5 | 0.29 | 8.6 (1.30) | 4.4 (1.98) | 4.0 (1.47) | 3.9 (1.25) |
| run-412 | 37 | 100 % | 7.1 / 9.0 | 0.39 | 15.4 (1.57) | 6.8 (2.14) | 6.9 (1.56) | 6.9 (1.46) |
| **mean** | | 100 % | 5.8 / 7.8 | 0.35 | 13.0 (1.41) | 5.8 (1.89) | 5.7 (1.42) | 5.7 (1.33) |

Compare the anchor error with simulate_<arm>.md: that table gives the trajectory error to expect for a given anchor error.

Poses for poses.py: `python poses.py --ckpts /data2/u0137815/rgbd-us/runs/rpr-rgb-gap8-123XX-gru8/fold*/best.pt --source anchored-offline-scr-v2-4XXB-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB --test-root /data2/u0137815/rgbd-us/data/test_4XXB --out <folder for this test>` (or anchored-pgo-scr-v2-4XXB-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB, anchored-causal-scr-v2-4XXB-odometry-odo-classical-vo-test_4XXB-recover3-startanchor-test_4XXB).
