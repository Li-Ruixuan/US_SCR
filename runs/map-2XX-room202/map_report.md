# Map without a tracker: room-202 (train_2XX)

Room-scan poses built without a tracker (scr_map.py). Error against Polaris after one rigid alignment of the whole map on the points 1 m in front of each camera; scene points at 1 m = the error the training labels inherit; 1 s motion = error of the relative pose between frames 30 rows apart (no alignment).

| stage | frames added | mapped | scene points at 1 m, mm (median / p90) | camera position mm | rotation deg | 1 s motion mm (median / p90) | loss mm |
|---|---|---|---|---|---|---|---|
| round 1 (+ camera calibration) | 1180 | 1241/1777 (70 %) | 7.7 / 20.4 | 13.8 / 28.7 | 1.03 | 13.7 / 29.9 | 78.3 |
| round 2 (+ camera calibration) | 536 | 1777/1777 (100 %) | 9.5 / 23.2 | 22.6 / 39.5 | 1.48 | 14.6 / 47.1 | 38.6 |
| final pass (+ camera calibration) | 1681 | 1777/1777 (100 %) | 8.1 / 19.6 | 22.2 / 34.4 | 1.44 | 7.7 / 35.2 | 38.6 |
| pose graph (+ camera calibration) | 0 | 1777/1777 (100 %) | 4.0 / 9.4 | 11.2 / 13.5 | 0.69 | 2.5 / 6.2 | 38.6 |

Camera calibration from `runs/repro/map-3XX/map.json` (fixed, not fitted here: only the alignment uses this session's Polaris) (one fixed camera-frame transform, a property of the probe; Polaris sees the marker, the map the camera): 31.7 mm, 1.51 deg. Rows marked (+ camera calibration) include it. It is not in the labels; `scr_anchor.py track` applies it when placing the US images (network trained with `train --map runs/map-2XX-room202`, or `track --cam-calib runs/map-2XX-room202/map.json`).

Timing (map vs Polaris s ms later, same frames; median scene points mm / rotation deg): -200: 26.5 / 1.77, -167: 22.7 / 1.49, -133: 19.0 / 1.23, -100: 14.8 / 1.00, -67: 10.8 / 0.79, -33: 6.8 / 0.68, +0: 4.0 / 0.70, +33: 5.5 / 0.87, +67: 9.0 / 1.15, +100: 13.0 / 1.46, +133: 17.1 / 1.76, +167: 21.3 / 2.07, +200: 25.4 / 2.37. Best +5 ms (no timing offset).

Labels for training: `poses_room-202.json` (`scr_anchor.py train --map runs/map-2XX-room202`).
