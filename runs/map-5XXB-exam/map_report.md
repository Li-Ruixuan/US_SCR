# Map without a tracker: room-505 (test_5XXB)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 1737 | 1798/1798 (100 %) | 8.7 / 16.5 | 15.9 / 33.3 | 1.00 | 7.0 / 17.1 | 68.1 |
| final pass (+ camera calibration) | 1565 | 1798/1798 (100 %) | 9.2 / 16.9 | 15.8 / 31.2 | 0.96 | 6.8 / 17.6 | 68.1 |
| pose graph (+ camera calibration) | 0 | 1798/1798 (100 %) | 3.9 / 6.8 | 2.4 / 4.4 | 0.34 | 1.2 / 2.6 | 68.1 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXB-exam`, or `track --cam-calib runs/map-5XXB-exam/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 15.3 / 1.02, -167: 13.4 / 0.88, -133: 11.1 / 0.74, -100: 9.0 / 0.61, -67: 7.0 / 0.49, -33: 5.0 / 0.40, +0: 3.9 / 0.34, +33: 4.4 / 0.36, +67: 6.0 / 0.47, +100: 8.0 / 0.60, +133: 10.0 / 0.72, +167: 12.3 / 0.85, +200: 14.3 / 0.98. Best +6 ms (no timing offset).

Labels for training: `poses_room-505.json` (`scr_anchor.py train --map runs/map-5XXB-exam`).
