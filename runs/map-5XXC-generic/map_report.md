# Map without a tracker: room-506 (test_5XXC)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 2012 | 2073/2640 (79 %) | 6.3 / 12.0 | 6.9 / 12.8 | 0.49 | 5.6 / 11.9 | 76.5 |
| round 2 (+ camera calibration) | 554 | 2627/2640 (100 %) | 7.5 / 12.6 | 7.7 / 13.6 | 0.47 | 5.4 / 12.8 | 35.2 |
| round 3 (+ camera calibration) | 3 | 2630/2640 (100 %) | 7.5 / 12.6 | 7.8 / 13.6 | 0.48 | 5.4 / 12.9 | 26.6 |
| final pass (+ camera calibration) | 2565 | 2630/2640 (100 %) | 6.0 / 10.3 | 6.1 / 10.0 | 0.33 | 2.8 / 7.1 | 26.6 |
| pose graph (+ camera calibration) | 0 | 2630/2640 (100 %) | 3.8 / 7.9 | 5.2 / 7.0 | 0.44 | 1.3 / 3.2 | 26.6 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-5XXC-generic`, or `track --cam-calib runs/map-5XXC-generic/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 13.8 / 1.22, -167: 11.8 / 1.05, -133: 9.9 / 0.88, -100: 8.2 / 0.76, -67: 6.3 / 0.62, -33: 4.7 / 0.50, +0: 3.6 / 0.40, +33: 4.1 / 0.36, +67: 5.7 / 0.40, +100: 7.5 / 0.49, +133: 9.4 / 0.60, +167: 11.3 / 0.74, +200: 13.1 / 0.87. Best +7 ms (no timing offset).

Labels for training: `poses_room-506.json` (`scr_anchor.py train --map runs/map-5XXC-generic`).
