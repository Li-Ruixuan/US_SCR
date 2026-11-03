# Map without a tracker: room-301 (train_3XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 1239 | 1300/1569 (83 %) | 9.9 / 26.9 | 14.2 / 38.0 | 1.09 | 11.6 / 36.3 | 74.1 |
| round 2 (+ camera calibration) | 269 | 1569/1569 (100 %) | 10.7 / 24.9 | 14.5 / 37.7 | 1.27 | 11.6 / 36.9 | 40.9 |
| final pass (+ camera calibration) | 1569 | 1569/1569 (100 %) | 8.9 / 19.4 | 10.5 / 28.4 | 1.01 | 9.4 / 23.9 | 40.9 |
| pose graph (+ camera calibration) | 0 | 1569/1569 (100 %) | 2.6 / 5.7 | 2.2 / 7.4 | 0.23 | 1.9 / 5.9 | 40.9 |

Camera calibration from the room scan (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 33.0 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-3XX-room301`, or `track --cam-calib runs/map-3XX-room301/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 24.5 / 1.63, -167: 21.1 / 1.37, -133: 17.2 / 1.13, -100: 13.2 / 0.87, -67: 9.2 / 0.64, -33: 5.5 / 0.42, +0: 2.6 / 0.23, +33: 4.3 / 0.35, +67: 8.1 / 0.57, +100: 11.9 / 0.82, +133: 15.8 / 1.07, +167: 19.6 / 1.32, +200: 23.7 / 1.57. Best +5 ms (no timing offset).

Labels for training: `poses_room-301.json` (`scr_anchor.py train --map runs/map-3XX-room301`).
