# Map without a tracker: room-201 (train_2XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 1387 | 1448/3589 (40 %) | 12.4 / 22.9 | 17.5 / 33.8 | 1.21 | 14.3 / 40.6 | 86.8 |
| round 2 (+ camera calibration) | 2101 | 3549/3589 (99 %) | 13.7 / 26.6 | 19.4 / 45.8 | 1.43 | 19.6 / 64.1 | 47.0 |
| round 3 (+ camera calibration) | 39 | 3588/3589 (100 %) | 13.8 / 26.7 | 19.7 / 45.5 | 1.46 | 20.0 / 64.5 | 39.0 |
| round 4 (+ camera calibration) | 1 | 3589/3589 (100 %) | 13.8 / 26.7 | 19.7 / 45.5 | 1.46 | 20.0 / 64.5 | 33.0 |
| final pass (+ camera calibration) | 3545 | 3589/3589 (100 %) | 11.3 / 21.5 | 14.7 / 33.4 | 1.18 | 13.8 / 38.7 | 33.0 |
| pose graph (+ camera calibration) | 0 | 3589/3589 (100 %) | 6.6 / 14.1 | 5.0 / 17.9 | 0.52 | 4.8 / 31.2 | 33.0 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-2XX-room201`, or `track --cam-calib runs/map-2XX-room201/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 45.7 / 2.89, -167: 39.3 / 2.48, -133: 32.3 / 2.04, -100: 25.0 / 1.60, -67: 18.1 / 1.16, -33: 11.3 / 0.76, +0: 6.6 / 0.52, +33: 9.2 / 0.73, +67: 15.8 / 1.16, +100: 22.5 / 1.63, +133: 29.2 / 2.09, +167: 36.3 / 2.55, +200: 43.1 / 3.02. Best +5 ms (no timing offset).

Labels for training: `poses_room-201.json` (`scr_anchor.py train --map runs/map-2XX-room201`).
